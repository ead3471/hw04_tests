from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        names = [
            'about:author',
            'about:tech'
        ]

        for name in names:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_about_pages_uses_correct_template(self):
        template_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

        for url, template in template_pages_names.items():
            with self.subTest(url=url, template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
