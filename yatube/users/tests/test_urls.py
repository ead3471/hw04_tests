from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class UsersUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.auth_user = User.objects.create_user("auth_user")

    def setUp(self) -> None:
        super().setUp()
        self.auth_client = Client()
        self.auth_client.force_login(UsersUrlsTest.auth_user)

    def test_unauth_user_access(self):
        urls_for_check = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_change/': HTTPStatus.FOUND,
            '/auth/password_change/done/': HTTPStatus.FOUND,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK
        }

        for url, expected_status in urls_for_check.items():
            with self.subTest(url=url, expected_status=expected_status):
                response = UsersUrlsTest.guest_client.get(url)
                self.assertEquals(response.status_code, expected_status)

    def test_unauth_user_redirect(self):
        urls_for_check = {
            '/auth/password_change/': '/auth/login/',
            '/auth/password_change/done/': '/auth/login/',
        }

        for url, redirect_url in urls_for_check.items():
            with self.subTest(url=url, redirect_url=redirect_url):
                full_redirect_url = redirect_url + "?next=" + url
                responce = self.guest_client.get(url, follow=True)
                self.assertRedirects(responce, full_redirect_url)

    def test_auth_user_access(self):
        urls_for_check = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
        }

        for url, expected_status in urls_for_check.items():
            with self.subTest(url=url, expected_status=expected_status):
                response = self.auth_client.get(url)
                self.assertEquals(response.status_code, expected_status)

    def test_templates(self):
        urls_for_check = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for url, template in urls_for_check.items():
            with self.subTest(url=url, template=template):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
