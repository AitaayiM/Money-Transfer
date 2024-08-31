from django.urls import path
from .views import (
    process_transaction, create_transaction, list_received_transactions
)

urlpatterns = [
    path('transactions/create/', create_transaction, name='transaction-create'),
    path('transactions/list_received/', list_received_transactions, name='transaction-received-list'),
    path('transactions/<int:pk>/process/', process_transaction, name='process-transaction'),

]
