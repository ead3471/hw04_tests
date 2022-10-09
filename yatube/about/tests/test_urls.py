from django.test import TestCase, Client
from http import HTTPStatus


class AboutUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guest_client = Client()
        super().setUpClass()

    def test_http_statuses(self):
        urls_for_check = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }

        for url, status in urls_for_check.items():
            with self.subTest(url=url, status=status):
                responce = AboutUrlsTest.guest_client.get(url)
                self.assertEquals(responce.status_code, status)

    def test_templates(self):
        urls_for_check = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

        for url, template in urls_for_check.items():
            with self.subTest(url=url, status=template):
                responce = AboutUrlsTest.guest_client.get(url)
                self.assertTemplateUsed(responce, template)
