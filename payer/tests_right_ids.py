"""
Payer's rights must not overlap another module's.

`gql_mutation_payer_update_perms` used to be 122103, which is medical's
`gql_mutation_medical_items_update_perms`. Because a right is just an integer on a
role, the two were indistinguishable: granting payer update also granted medical item
edit, and vice versa. Payer owns 1218xx (121801 search, 121802 add, 121804 delete) and
121803 was the free slot for update, so that is what it now uses.

These assertions are cheap and pin the separation in both directions - the ids, and the
behaviour of a user holding only one of them.
"""

from django.test import TestCase

from core.test_helpers import create_right_only_user, resolve_perm_right_ids
from medical.apps import MedicalConfig
from payer.apps import PayerConfig

PAYER_UPDATE = "gql_mutation_payer_update_perms"
MEDICAL_ITEMS_UPDATE = "gql_mutation_medical_items_update_perms"


class PayerRightIdTestCase(TestCase):
    def test_payer_update_right_id(self):
        self.assertEqual(PayerConfig.gql_mutation_payer_update_perms, ["121803"])

    def test_payer_update_sits_in_the_payer_block(self):
        """All four payer rights belong to 1218xx."""
        for perm_name in (
            "gql_query_payers_perms",
            "gql_mutation_payer_add_perms",
            PAYER_UPDATE,
            "gql_mutation_payer_delete_perms",
        ):
            with self.subTest(perm_name=perm_name):
                for right_id in getattr(PayerConfig, perm_name):
                    self.assertTrue(
                        right_id.startswith("1218"),
                        f"{perm_name} = {right_id}, outside payer's 1218xx block",
                    )

    def test_payer_update_is_not_medical_items_update(self):
        self.assertNotEqual(
            PayerConfig.gql_mutation_payer_update_perms,
            MedicalConfig.gql_mutation_medical_items_update_perms,
        )
        self.assertEqual(
            set(resolve_perm_right_ids([PAYER_UPDATE]))
            & set(resolve_perm_right_ids([MEDICAL_ITEMS_UPDATE])),
            set(),
        )

    def test_payer_update_right_does_not_grant_medical_item_edit(self):
        user = create_right_only_user("r_payr_upd", [PAYER_UPDATE])
        self.assertTrue(user.has_perms(PayerConfig.gql_mutation_payer_update_perms))
        self.assertFalse(
            user.has_perms(MedicalConfig.gql_mutation_medical_items_update_perms),
            "payer update must not carry medical item edit",
        )

    def test_medical_item_edit_right_does_not_grant_payer_update(self):
        user = create_right_only_user("r_med_upd", [MEDICAL_ITEMS_UPDATE])
        self.assertTrue(
            user.has_perms(MedicalConfig.gql_mutation_medical_items_update_perms)
        )
        self.assertFalse(
            user.has_perms(PayerConfig.gql_mutation_payer_update_perms),
            "medical item edit must not carry payer update",
        )
