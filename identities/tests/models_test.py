from django.test import TestCase
from identities.models import Profile, User, Role, Roles

class UserModelTestCase(TestCase):
    def test_create_user(self):
        # Créer les rôles
        sender_role = Role.objects.create(name=Roles.SENDER)
        receiver_role = Role.objects.create(name=Roles.RECEIVER)
        # Créer un utilisateur
        user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='johndoe@example.com',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password'
        )
        # Ajouter les rôles à l'utilisateur
        user.roles.add(sender_role)
        user.roles.add(receiver_role)
        # Vérifier que l'utilisateur est créé correctement
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.username, 'johndoe@example.com')
        self.assertEqual(user.date_of_birth, '1990-01-01')
        self.assertEqual(user.gender, 'Male')
        self.assertTrue(user.roles.filter(name=Roles.SENDER).exists())
        self.assertTrue(user.roles.filter(name=Roles.RECEIVER).exists())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        # Vérifier que le profil est créé pour cet utilisateur
        self.assertIsNotNone(user.profile)
        self.assertIsInstance(user.profile, Profile)

    def test_create_superuser(self):
        # Créer les rôles
        admin_role = Role.objects.create(name=Roles.AGENT)
        # Créer un superutilisateur
        superuser = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            username='admin@example.com',
            date_of_birth='1980-01-01',
            gender='Male',
            password='adminpassword'
        )
        # Ajouter le rôle admin à l'utilisateur
        superuser.roles.add(admin_role)
        # Vérifier que le superutilisateur est créé correctement
        self.assertEqual(superuser.first_name, 'Admin')
        self.assertEqual(superuser.last_name, 'User')
        self.assertEqual(superuser.username, 'admin@example.com')
        self.assertEqual(superuser.date_of_birth, '1980-01-01')
        self.assertEqual(superuser.gender, 'Male')
        self.assertTrue(superuser.roles.filter(name=Roles.AGENT).exists())
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_admin)
        # Vérifier que le profil est créé pour le superutilisateur
        self.assertIsNotNone(superuser.profile)
        self.assertIsInstance(superuser.profile, Profile)