from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from ..models import Post, Group
from http import HTTPStatus

User = get_user_model()


class PostUrlsTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title="TestGroup",
            slug="TestGroupSlug",
            description="TestGroupdescription"
        )

        cls.post_author_user = User.objects.create_user("post_author")
        cls.not_post_author_user = User.objects.create_user("not_post_author")

        cls.test_post = Post.objects.create(
            text='Test text',
            author=cls.post_author_user,
            group=cls.test_group
        )

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

        self.post_author_client = Client()
        self.post_author_client.force_login(PostUrlsTests.post_author_user)

        self.not_post_author_client = Client()
        self.not_post_author_client.force_login(
            PostUrlsTests.not_post_author_user)

    def test_unauth_user_access(self):
        urls_for_check = {
            "/": HTTPStatus.OK,

            f"/group/{PostUrlsTests.test_group.slug}/": HTTPStatus.OK,

            (f"/profile/{PostUrlsTests.post_author_user.username}/"):
                HTTPStatus.OK,

            f"/posts/{PostUrlsTests.test_post.id}/": HTTPStatus.OK,

            "/create/": HTTPStatus.FOUND,

            f"/posts/{PostUrlsTests.test_post.id}/edit/": HTTPStatus.FOUND,

            "/unexisting_page/": HTTPStatus.NOT_FOUND
        }

        for url, status_code in urls_for_check.items():
            with self.subTest(url=url, status_code=status_code):
                responce = self.guest_client.get(url)
                self.assertEqual(responce.status_code, status_code)

    def test_post_author_access(self):
        urls_for_check = {
            "/":
                HTTPStatus.OK,

            f"/group/{PostUrlsTests.test_group.slug}/": HTTPStatus.OK,

            f"/profile/{PostUrlsTests.post_author_user.username}/":
                HTTPStatus.OK,

            f"/posts/{PostUrlsTests.test_post.id}/":
                HTTPStatus.OK,

            "/create/":
                HTTPStatus.OK,

            f"/posts/{PostUrlsTests.test_post.id}/edit/":
                HTTPStatus.OK,

            "/unexisting_page/":
                HTTPStatus.NOT_FOUND,

        }

        for url, status_code in urls_for_check.items():
            with self.subTest(url=url, status_code=status_code):
                responce = self.post_author_client.get(url)
                self.assertEqual(responce.status_code, status_code)

    def test_post_author_templates(self):
        urls_for_check = {
            "/": "posts/index.html",

            f"/group/{PostUrlsTests.test_group.slug}/":
                "posts/group_list.html",

            f"/profile/{PostUrlsTests.post_author_user.username}/":
                "posts/profile.html",

            f"/posts/{PostUrlsTests.test_post.id}/":
                "posts/post_detail.html",

            "/create/":
                "posts/create_post.html",

            f"/posts/{PostUrlsTests.test_post.id}/edit/":
                "posts/create_post.html",
        }

        for url, template in urls_for_check.items():
            with self.subTest(url=url, template=template):
                responce = self.post_author_client.get(url)
                self.assertTemplateUsed(responce, template)

    def test_guest_user_redirect(self):
        urls_for_check = {
            "/create/":
                "/auth/login/",

            f"/posts/{PostUrlsTests.test_post.id}/edit/":
                "/auth/login/"
        }

        for url, redirect_url in urls_for_check.items():
            with self.subTest(url=url, redirect_url=redirect_url):
                full_redirect_url = redirect_url + "?next=" + url
                responce = self.guest_client.get(url, follow=True)
                self.assertRedirects(responce, full_redirect_url)

    def test_not_post_author_redirect(self):
        urls_for_check = {
            f"/posts/{PostUrlsTests.test_post.id}/edit/":
                f"/posts/{PostUrlsTests.test_post.id}/"
        }

        for url, redirect_url in urls_for_check.items():
            with self.subTest(url=url, redirect_url=redirect_url):
                responce = self.not_post_author_client.get(url, follow=True)
                self.assertRedirects(responce, redirect_url)
