from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
from identities.models import User

class Status(models.TextChoices):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    PROCESSED = 'Processed'
    COMPLETED = 'Completed'

class Transaction(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    agent = models.ForeignKey(User, related_name='processed_transactions', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    encrypted_data = models.BinaryField()

    def save(self, *args, **kwargs):
        fernet = Fernet(settings.ENCRYPTION_KEY)
        # Convertir l'objet Decimal en chaîne avant de l'encoder
        amount_str = str(self.amount)
        self.encrypted_data = fernet.encrypt(amount_str.encode())
        super().save(*args, **kwargs)
