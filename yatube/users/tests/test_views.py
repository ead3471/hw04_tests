from http import HTTPStatus
from typing import Callable, Dict
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

User = get_user_model()


class TestUserPages(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.auth_user = User.objects.create_user("new_user")

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(TestUserPages.auth_user)

    def check_responses_with_dict_of_urls(self,
                                          client: Client,
                                          response_check_function: Callable,
                                          urls_dict: Dict):
        for url, expected_value in urls_dict.items():
            with self.subTest(url=url, expected_value=expected_value):
                response = client.get(url)
                response_check_function(response, expected_value)

    def test_user_pages_accesible_by_name_for_guest(self):
        urls_to_check = {
            reverse('users:password_change_form'): HTTPStatus.FOUND,
            reverse('users:password_change_done'): HTTPStatus.FOUND,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK

        }

        def check_function(response, expected_value):
            self.assertEquals(response.status_code, expected_value)

        self.check_responses_with_dict_of_urls(self.guest_client,
                                               check_function,
                                               urls_to_check)

    def test_user_pages_accesible_by_name_for_user(self):
        urls_to_check = {
            reverse('users:password_change_form'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK

        }

        def check_function(response, expected_value):
            self.assertEquals(response.status_code, expected_value)

        self.check_responses_with_dict_of_urls(self.auth_client,
                                               check_function,
                                               urls_to_check)

    def test_user_pages_templates_for_guest(self):
        urls_to_check = {
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',

            reverse('users:password_reset_done'):
                'users/password_reset_done.html',

            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',

            reverse('users:signup'):
                'users/signup.html',

            reverse('users:login'):
                'users/login.html',

            reverse('users:logout'):
                'users/logged_out.html',
        }

        def check_function(response, expected_value):
            self.assertTemplateUsed(response, expected_value)

        self.check_responses_with_dict_of_urls(self.guest_client,
                                               check_function,
                                               urls_to_check)

    def test_signup_uses_right_form(self):
        response = self.guest_client.get(reverse('users:signup'))

        fields = {
            'first_name': forms.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.EmailField,
            'password1': forms.CharField,
            'password2': forms.CharField
        }

        for field_name, expected_type in fields.items():
            with self.subTest(field_name=field_name,
                              expected_type=expected_type):
                field = response.context.get("form").fields.get(field_name)
                self.assertIsInstance(field, expected_type)
            

        form = response



    def test_user_pages_templates_for_auth_client(self):
        urls_to_check = {
            reverse('users:password_change_form'):
                'users/password_change_form.html',

            reverse('users:password_change_done'):
                'users/password_change_done.html',

            reverse('users:password_reset_form'):
                'users/password_reset_form.html',

            reverse('users:password_reset_done'):
                'users/password_reset_done.html',

            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',

            reverse('users:signup'):
                'users/signup.html',

            reverse('users:login'):
                'users/login.html',

            reverse('users:logout'):
                'users/logged_out.html',
        }

        def check_function(response, expected_value):
            self.assertTemplateUsed(response, expected_value)

        self.check_responses_with_dict_of_urls(self.auth_client,
                                               check_function,
                                               urls_to_check)