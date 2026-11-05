"""get_queryset honours the OP-2029 validity contract (epic OP-3317, phase 1).

Explicit validity values return the expected rows; a caller asking for
nothing gets what it got before the contract existed.
"""

from django.test import TestCase

from core.test_helpers import assert_row_filters, create_test_interactive_user, mark_deleted
from payer.models import Payer
from payer.test_helpers import create_test_payer


class PayerRowFiltersTest(TestCase):
    def test_payer(self):
        user = create_test_interactive_user(username="payerrowfilters")
        live = create_test_payer()
        deleted = mark_deleted(create_test_payer())
        assert_row_filters(
            self, Payer, Payer.objects.filter(id__in=[live.id, deleted.id]), user,
            live.id, deleted.id, default_hides_deleted=True,
        )
