import base64
import json
from dataclasses import dataclass

from core.models import User
from core.test_helpers import create_test_interactive_user
from django.conf import settings
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from location.models import Location
from location.test_helpers import create_test_location, assign_user_districts
from rest_framework import status
from insuree.test_helpers import create_test_insuree
from location.test_helpers import create_test_location, create_test_health_facility, create_test_village



# from openIMIS import schema


@dataclass
class DummyContext:
    """ Just because we need a context to generate. """
    user: User


class PayerGQLTestCase(GraphQLTestCase):
    GRAPHQL_URL = f'/{settings.SITE_ROOT()}graphql'
    # This is required by some version of graphene but is never used. It should be set to the schema but the import
    # is shown as an error in the IDE, so leaving it as True.
    GRAPHQL_SCHEMA = True
    admin_user = None
    ca_user = None
    ca_token = None
    test_village = None
    test_insuree = None
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_village = create_test_village()
        cls.test_insuree = create_test_insuree(with_family=True, is_head=True, custom_props={'current_village':cls.test_village}, family_custom_props={'location':cls.test_village})
        cls.admin_user = create_test_interactive_user(username="testLocationAdmin")
        cls.admin_token = get_token(cls.admin_user, DummyContext(user=cls.admin_user))
        cls.ca_user = create_test_interactive_user(username="testLocationNoRight", roles=[9])
        cls.ca_token = get_token(cls.ca_user, DummyContext(user=cls.ca_user))
        cls.admin_dist_user = create_test_interactive_user(username="testLocationDist")
        assign_user_districts(cls.admin_dist_user, ["R1D1", "R2D1", "R2D2", "R2D1", cls.test_village.parent.parent.code])
        cls.admin_dist_token = get_token(cls.admin_dist_user, DummyContext(user=cls.admin_dist_user))

    def test_query_insuree_number_validity(self):
        response = self.query(
            '''
  query usePayersQuery (
    $first: Int, $last: Int, $before: String, $after: String, $phone: String, $name: String,
    $email: String, $location: Int, $showHistory: Boolean, $search: String, $type: PayerType,
    ) {
    payers (
      first: $first, last: $last, before: $before, after: $after, phone_Icontains: $phone, showHistory: $showHistory, type: $type
      name_Icontains: $name, location: $location, email_Icontains: $email, search: $search
      ) {
      edges {
        node {
          id
          uuid
          ...PayerFragment
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }

  fragment PayerFragment on PayerGQLType {
    id
    uuid
    name
    email
    phone
    type
    address
    location {id name uuid code parent {id name uuid code}}
    validityFrom
    validityTo
  } 
            ''',
            headers={"HTTP_AUTHORIZATION": f"Bearer {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        



