from django.test import TestCase, Client
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.forms.fields import Field
from django.utils.encoding import force_text
from django.conf import settings
from django.contrib.auth import SESSION_KEY

from accounts.forms import PasswordResetForm, RegisterForm, AuthenticationForm


class TestCaseWithUser(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'secret'
        self.user = User.objects.create_user(
            username='jacob',
            email='jacob@example.com',
            password=self.password)


class AuthenticatedTestCase(TestCaseWithUser):
    def login(self):
        form_data = {'username': self.user.username, 'password': self.password}
        response = self.client.post(reverse('accounts:login'), form_data)
        self.assertTrue(SESSION_KEY in self.client.session)
        return response


class ProfileView(AuthenticatedTestCase):
    def test_get(self):
        """
        Test that the profile contains the profile form.
        """
        self.login()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_update(self):
        """
        Test that a user can update his profile successfully.
        """
        self.login()
        form_data = {'first_name': 'Jacob', 'last_name': 'User',
                     'email': 'jacob@example.com'}
        response = self.client.post(reverse('accounts:profile'), form_data)
        self.assertRedirects(response, reverse('accounts:profile'),
                             status_code=302, target_status_code=200)
        user = User.objects.get_by_natural_key(self.user.username)
        self.assertEqual(user.first_name, 'Jacob')
        self.assertEqual(user.last_name, 'User')

    def test_cant_change_username(self):
        """
        Test that a user cannot update his username through profile.
        """
        self.login()
        form_data = {'username': 'hacked', 'email': 'jacob@example.com'}
        response = self.client.post(reverse('accounts:profile'), form_data)
        self.assertRedirects(response, reverse('accounts:profile'),
                             status_code=302, target_status_code=200)
        with self.assertRaises(User.DoesNotExist):
            user = User.objects.get_by_natural_key('hacked')


class LogoutView(AuthenticatedTestCase):
    def test_get(self):
        """
        Test that the logout page works and redirects to login page.
        """
        self.login()
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'),
                             status_code=302, target_status_code=200)
        self.assertTrue(SESSION_KEY not in self.client.session)


class LoginView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the login page contains the login form.
        """
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_valid(self):
        """
        Test that a valid login gets redirected to the home page.
        """
        form_data = {'username': self.user.username, 'password': self.password}
        response = self.client.post(reverse('accounts:login'), form_data)
        self.assertTrue(SESSION_KEY in self.client.session)
        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200)

    def test_invalid(self):
        """
        Test that an invalid login does not work.
        """
        form_data = {'username': 'bad', 'password': 'bad'}
        response = self.client.post(reverse('accounts:login'), form_data)
        self.assertTrue(SESSION_KEY not in self.client.session)
        self.assertFormError(
            response,
            'form',
            '__all__',
            AuthenticationForm.error_messages['invalid_login'] % {
                'username': User._meta.get_field('username').verbose_name
            })


class RegisterView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the register page contains the register form.
        """
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_invalid(self):
        """
        Test that all required fields are enforced.
        """
        form_data = {'username': ''}
        response = self.client.post(reverse('accounts:register'), form_data)
        required_error = force_text(Field.default_error_messages['required'])
        self.assertFormError(response, 'form', 'username', required_error)
        self.assertFormError(response, 'form', 'auth_code', required_error)
        self.assertFormError(response, 'form', 'username', required_error)
        self.assertFormError(response, 'form', 'email', required_error)
        self.assertFormError(response, 'form', 'password1', required_error)

    def test_duplicate_fields(self):
        """
        Test that username and email must be unique.
        """
        form_data = {'username': self.user.username, 'email': self.user.email}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertFormError(response, 'form', 'username',
                             RegisterForm.error_messages['duplicate_username'])
        self.assertFormError(response, 'form', 'email',
                             RegisterForm.error_messages['duplicate_email'])

    def test_valid_auth_code_user(self):
        """
        Test that valid authorization code works for user.
        """
        form_data = {'username': 'uniq', 'email': 'uniq@example.com',
                     'password1': 'welcome', 'password2': 'welcome',
                     'auth_code': settings.AUTH_CODE_USER}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertRedirects(response, reverse('accounts:login'),
                             status_code=302, target_status_code=200)
        uniq = User.objects.get_by_natural_key('uniq').groups.all()
        self.assertEqual(uniq.count(), 0)

    def test_valid_auth_code_admin(self):
        """
        Test that valid authorization code works for admin.
        """
        form_data = {'username': 'uniq', 'email': 'uniq@example.com',
                     'password1': 'welcome', 'password2': 'welcome',
                     'auth_code': settings.AUTH_CODE_ADMIN}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertRedirects(response, reverse('accounts:login'),
                             status_code=302, target_status_code=200)
        uniq = User.objects.get_by_natural_key('uniq').groups.all()
        self.assertEqual(uniq.count(), 1)
        self.assertEqual(uniq[0], Group.objects.get(
            name=settings.AUTH_CODE_ADMIN_GROUP))

    def test_invalid_auth(self):
        """
        Test that otherwise valid forms do not work with an invalid auth code.
        """
        form_data = {'username': 'uniq', 'email': 'uniq@example.com',
                     'password1': 'welcome', 'password2': 'welcome',
                     'auth_code': 'fake'}
        response = self.client.post(reverse('accounts:register'), form_data)
        self.assertFormError(response, 'form', 'auth_code',
                             RegisterForm.error_messages['invalid_auth_code'])


class PasswordResetView(TestCaseWithUser):
    def test_get(self):
        """
        Test that the password reset page contains the form.
        """
        response = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_invalid(self):
        """
        Test that invalid email addresses will be caught.
        """
        form_data = {'email': 'invalid@invalid.com'}
        response = self.client.post(reverse('accounts:password_reset'),
                                    form_data)
        self.assertFormError(response, 'form', 'email',
                             PasswordResetForm.error_messages['invalid_email'])
        self.assertEqual(len(mail.outbox), 0)

    def test_valid(self):
        """
        Test that the valid email addresses will get an email.
        """
        form_data = {'email': self.user.email}
        response = self.client.post(reverse('accounts:password_reset'),
                                    form_data)
        self.assertRedirects(response, reverse('accounts:login'),
                             status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue('http://' in mail.outbox[0].body)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL,
                         mail.outbox[0].from_email)
