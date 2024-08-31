from celery import shared_task
from .models import Transaction
from django.core.mail import send_mail


@shared_task
def process_transaction_task(transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Envoyer un e-mail de confirmation
        send_mail(
            'Transaction Confirmed',
            f'Your transaction to {transaction.receiver.first_name+" "+transaction.receiver.last_name} has been processed successfully.',
            'noreply@moneytransfer.com',
            [transaction.sender.username],
        )
        return True
    except Transaction.DoesNotExist:
        return False
