"""Row security on payers and fundings (OP-3322).

A payer is visible when its location sits in the user's districts, or when it
has no location at all. Reads by uuid, the connection, and every mutation
target go through that same scope.
"""

import datetime
import json

from core.models.openimis_graphql_test_case import (
    BaseTestContext,
    openIMISGraphQLTestCase,
)
from core.test_helpers import create_right_only_user
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from graphql_jwt.shortcuts import get_token
from location.models import Location
from location.test_helpers import create_basic_test_locations
from product.test_helpers import create_test_product

from payer.gql_mutations import (
    AddFundingMutation,
    CreatePayerMutation,
    DeletePayerMutation,
    UpdatePayerMutation,
)
from payer.models import Funding, Payer
from payer.test_helpers import create_test_payer

PAYER_PERMS = [
    "gql_query_payers_perms",
    "gql_mutation_payer_add_perms",
    "gql_mutation_payer_update_perms",
    "gql_mutation_payer_delete_perms",
]


class PayerRowSecurityTest(openIMISGraphQLTestCase):
    GRAPHQL_URL = f"/{settings.SITE_ROOT()}graphql"
    GRAPHQL_SCHEMA = True

    @classmethod
    def setUpTestData(cls):
        create_basic_test_locations()
        cls.own_district = Location.objects.get(code="R2D1", validity_to__isnull=True)
        cls.other_district = Location.objects.get(code="R1D1", validity_to__isnull=True)
        cls.user = create_right_only_user(
            "payerRowSecUser", PAYER_PERMS, district_codes=["R2D1"]
        )
        cls.token = get_token(cls.user, BaseTestContext(user=cls.user))
        cls.own_payer = create_test_payer(
            custom_props={"name": "own payer", "location": cls.own_district}
        )
        cls.other_payer = create_test_payer(
            custom_props={"name": "other payer", "location": cls.other_district}
        )
        cls.national_payer = create_test_payer(custom_props={"name": "national payer"})
        cls.product = create_test_product("PAYRS")
        cls.other_funding = Funding(
            payer=cls.other_payer,
            product=cls.product,
            pay_date=datetime.date(2024, 1, 1),
            amount=10,
            receipt="RS-1",
        )
        cls.other_funding.save(username=cls.user.username)

    def _visible(self, queryset=None):
        if queryset is None:
            queryset = Payer.objects.all()
        return set(Payer.get_queryset(queryset, self.user).values_list("id", flat=True))

    # -- model scope ------------------------------------------------------------

    def test_scope_keeps_own_district_and_no_location(self):
        visible = self._visible()
        self.assertIn(self.own_payer.id, visible)
        self.assertIn(self.national_payer.id, visible)
        self.assertNotIn(self.other_payer.id, visible)

    def test_scope_keeps_the_incoming_queryset(self):
        visible = self._visible(Payer.objects.filter(id=self.national_payer.id))
        self.assertEqual({self.national_payer.id}, visible)

    def test_anonymous_user_sees_nothing_and_does_not_crash(self):
        queryset = Payer.get_queryset(Payer.objects.all(), AnonymousUser())
        self.assertFalse(queryset.exists())

    def test_funding_follows_its_payer(self):
        visible = Funding.get_queryset(Funding.objects.all(), self.user)
        self.assertFalse(visible.filter(id=self.other_funding.id).exists())

    # -- GraphQL reads ----------------------------------------------------------

    def _gql(self, query, variables=None):
        response = self.query(
            query,
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.token}"},
            variables=variables or {},
        )
        self.assertResponseNoErrors(response)
        return json.loads(response.content)["data"]

    def test_payer_by_uuid_outside_scope_is_not_found(self):
        data = self._gql(
            "query ($uuid: UUID) { payer(uuid: $uuid) { name } }",
            {"uuid": str(self.other_payer.uuid)},
        )
        self.assertIsNone(data["payer"])

    def test_payer_by_uuid_inside_scope_is_found(self):
        data = self._gql(
            "query ($uuid: UUID) { payer(uuid: $uuid) { name } }",
            {"uuid": str(self.own_payer.uuid)},
        )
        self.assertEqual("own payer", data["payer"]["name"])

    def test_funding_by_uuid_outside_scope_is_not_found(self):
        data = self._gql(
            "query ($uuid: UUID) { funding(uuid: $uuid) { receipt } }",
            {"uuid": str(self.other_funding.id)},
        )
        self.assertIsNone(data["funding"])

    def test_payers_connection_is_scoped(self):
        data = self._gql("{ payers { edges { node { name } } } }")
        names = {edge["node"]["name"] for edge in data["payers"]["edges"]}
        self.assertIn("own payer", names)
        self.assertIn("national payer", names)
        self.assertNotIn("other payer", names)

    # -- mutations --------------------------------------------------------------

    def test_update_of_a_payer_outside_scope_is_refused(self):
        errors = UpdatePayerMutation.async_mutate(
            self.user,
            uuid=self.other_payer.uuid,
            name="hijacked",
            type=Payer.PAYER_TYPE_OTHER,
            location_uuid=self.own_district.uuid,
        )
        self.assertTrue(errors)
        self.other_payer.refresh_from_db()
        self.assertEqual("other payer", self.other_payer.name)

    def test_update_moving_a_payer_outside_scope_is_refused(self):
        errors = UpdatePayerMutation.async_mutate(
            self.user,
            uuid=self.own_payer.uuid,
            name="own payer",
            type=Payer.PAYER_TYPE_OTHER,
            location_uuid=self.other_district.uuid,
        )
        self.assertTrue(errors)
        self.own_payer.refresh_from_db()
        self.assertEqual(self.own_district.id, self.own_payer.location_id)

    def test_create_at_a_location_outside_scope_is_refused(self):
        errors = CreatePayerMutation.async_mutate(
            self.user,
            name="created elsewhere",
            type=Payer.PAYER_TYPE_OTHER,
            location_uuid=self.other_district.uuid,
        )
        self.assertTrue(errors)
        self.assertFalse(Payer.objects.filter(name="created elsewhere").exists())

    def test_create_in_own_district_is_accepted(self):
        errors = CreatePayerMutation.async_mutate(
            self.user,
            name="created at home",
            type=Payer.PAYER_TYPE_OTHER,
            location_uuid=self.own_district.uuid,
        )
        self.assertFalse(errors)
        self.assertTrue(Payer.objects.filter(name="created at home").exists())

    def test_delete_of_a_payer_outside_scope_is_refused(self):
        errors = DeletePayerMutation.async_mutate(
            self.user, uuids=[str(self.other_payer.uuid)]
        )
        self.assertTrue(errors)
        self.other_payer.refresh_from_db()
        self.assertIsNone(self.other_payer.validity_to)

    def test_add_funding_to_a_payer_outside_scope_is_refused(self):
        with self.assertRaises(Payer.DoesNotExist):
            AddFundingMutation.async_mutate(
                self.user,
                payer_id=self.other_payer.id,
                product_id=self.product.id,
                pay_date=datetime.date(2024, 2, 1),
                amount=5,
                receipt="RS-2",
            )
        self.assertFalse(Funding.objects.filter(receipt="RS-2").exists())
