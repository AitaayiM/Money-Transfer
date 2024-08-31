from django.test import SimpleTestCase
from django.urls import reverse, resolve
from transfers.views import (
    process_transaction, create_transaction, list_received_transactions
)

class TransfersTestUrls(SimpleTestCase):

    def test_create_transaction_url_resolves(self):
        url = reverse('transaction-create')
        self.assertEqual(resolve(url).func, create_transaction)

    def test_list_received_transactions_url_resolves(self):
        url = reverse('transaction-received-list')
        self.assertEqual(resolve(url).func, list_received_transactions)

    def test_process_transaction_url_resolves(self):
        url = reverse('process-transaction', args=[1])
        self.assertEqual(resolve(url).func, process_transaction)
