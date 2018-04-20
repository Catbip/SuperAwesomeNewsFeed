from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .forms import RegisterForm


class AuthenticationViewTests(TestCase):
    def setUp(self):
        User.objects.create_user('test', 'test@email.com', 'test1234')
        self.user = User.objects.get(username='test')

    def test_authentication_index_if_logged_in(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('authentication:index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url='/newsfeed/all/')

    def test_authentication_index_if_not_logged_in(self):
        response = self.client.get(reverse('authentication:index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url='/login/')

    def test_authentication_register(self):
        response = self.client.get(reverse('authentication:register'), {'Username': 'Test',
                                                                        'Email address': 'test@email.com',
                                                                        'Password': 'test1234'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/registration_form.html')

    def test_authentication_login_successful(self):
        response = self.client.post(reverse('authentication:login_user'), {'username': 'test', 'password': 'test1234'},
                                    follow=True)
        self.assertTrue(response.context['user'].is_active)
        self.assertTemplateUsed(response, 'newsfeed/newsfeed.html')

    def test_authentication_login_template(self):
        response = self.client.get(reverse('authentication:login_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login_form.html')

    def test_authentication_logout(self):
        response = self.client.get(reverse('authentication:logout_user'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url='/login/')


class AuthenticationFormsTests(TestCase):

    def test_registration_form_valid(self):
        form_data = {'username': 'Test', 'email': 'test@email.com', 'password': 'test1234'}
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_username(self):
        form_data = {'username': '', 'email': 'test@email.com', 'password': 'test1234'}
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_form_invalid_email(self):
        form_data = {'username': 'Test', 'email': 'test', 'password': 'test1234'}
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_form_invalid_password(self):
        form_data = {'username': 'Test', 'email': 'test@email.com', 'password': ''}
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
