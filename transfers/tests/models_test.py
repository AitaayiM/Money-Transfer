from django.test import TestCase
from identities.models import User, Roles, Role
from transfers.models import Transaction, Status
from django.utils import timezone

from money_transfer import settings


class TransactionModelTestCase(TestCase):

    def setUp(self):
        # Create Roles
        self.sender_role = Role.objects.create(name=Roles.SENDER)
        self.receiver_role = Role.objects.create(name=Roles.RECEIVER)
        self.agent_role = Role.objects.create(name=Roles.AGENT)

        # Create Users
        self.sender = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='sender@example.com',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password'
        )
        self.receiver = User.objects.create_user(
            first_name='Jane',
            last_name='Doe',
            username='receiver@example.com',
            date_of_birth='1992-02-02',
            gender='Female',
            password='password'
        )
        self.agent = User.objects.create_user(
            first_name='Agent',
            last_name='Smith',
            username='agent@example.com',
            date_of_birth='1988-03-03',
            gender='Male',
            password='password'
        )

        # Assign Roles
        self.sender.roles.add(self.sender_role)
        self.receiver.roles.add(self.receiver_role)
        self.agent.roles.add(self.agent_role)

        # Create a Transaction
        self.transaction = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            agent=self.agent,
            amount=100.00,
            status=Status.PENDING
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.sender, self.sender)
        self.assertEqual(self.transaction.receiver, self.receiver)
        self.assertEqual(self.transaction.agent, self.agent)
        self.assertEqual(self.transaction.amount, 100.00)
        self.assertEqual(self.transaction.status, Status.PENDING)

    def test_transaction_encryption(self):
        self.assertNotEqual(self.transaction.encrypted_data, None)
        # Decrypt to verify the amount was encrypted properly
        from cryptography.fernet import Fernet
        fernet = Fernet(settings.ENCRYPTION_KEY)
        decrypted_data = fernet.decrypt(self.transaction.encrypted_data).decode()
        self.assertEqual(decrypted_data, str(self.transaction.amount))

    def test_transaction_status_change(self):
        self.transaction.status = Status.PROCESSED
        self.transaction.save()
        self.assertEqual(self.transaction.status, Status.PROCESSED)

    def test_transaction_timestamps(self):
        self.assertIsInstance(self.transaction.created_at, timezone.datetime)
        self.assertIsInstance(self.transaction.updated_at, timezone.datetime)
