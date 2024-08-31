from django.test import SimpleTestCase
from django.urls import reverse, resolve
from identities.views import (
    register, login, login_verification, forgot_password,
    reset_password, get_all_users
)

class IdentityTestUrls(SimpleTestCase):

    def test_register_url_resolves(self):
        url = reverse('signup')
        self.assertEqual(resolve(url).func, register)

    def test_forgot_password_url_resolves(self):
        url = reverse('forgot_password')
        self.assertEqual(resolve(url).func, forgot_password)

    def test_reset_password_url_resolves(self):
        url = reverse('reset_password', args=['token'])
        self.assertEqual(resolve(url).func, reset_password)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login)

    def test_login_verification_url_resolves(self):
        url = reverse('verify')
        self.assertEqual(resolve(url).func, login_verification)

    def test_get_all_users_url_resolves(self):
        url = reverse('users')
        self.assertEqual(resolve(url).func, get_all_users)
