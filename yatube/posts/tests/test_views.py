import shutil
import tempfile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.core.paginator import Page
from django.contrib.auth import get_user_model

from ..forms import CommentForm
from ..models import Post, Group, Comment
from django.urls import reverse
from django import forms
from test_utils.utils import (check_responses_of_given_urls,
                              check_template,
                              check_form_fields_type)
from .utils import (check_posts_fields,
                    check_page_contains_post_on_first_position,
                    create_image,
                    compare_model_objects_list)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()

        cls.auth_user = User.objects.create_user("auth_user")
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.auth_user)

        cls.test_group = Group.objects.create(
            title="Test title",
            slug="Test_slug",
            description="Test description"
        )

        cls.test_post = Post.objects.create(
            text="Test text",
            group=cls.test_group,
            author=cls.auth_user
        )

        cls.tests_authors = []
        for author_number in range(3):
            new_author = User.objects.create_user(f"Author_{author_number}")
            cls.tests_authors.append(new_author)

        cls.tests_groups = []
        for group_number in range(3):
            cls.tests_groups.append(
                Group.objects.create(
                    title=f"Group {group_number} title",
                    slug=f"Group_{group_number}_slug",
                    description=f"Group_{group_number}_description"
                )
            )

        cls.tests_posts = []
        posts_in_groups_count = [3, 12, 0]

        group_number = 0

        # Создание от каждого автора постов в группах в соответствии"
        # с posts_in_group_count"
        for group in cls.tests_groups:
            posts_in_group = posts_in_groups_count.pop()
            for author in cls.tests_authors:
                for post_number in range(posts_in_group):
                    new_post = Post.objects.create(
                        author=author,
                        text=(f"Athor {author.username} post {post_number}"
                              f"in group {group.slug}"),
                        group=group,
                        image=create_image()
                    )
                    cls.tests_posts.append(new_post)

        for post in Post.objects.all():
            for comment_number in range(5):
                post_text = (f"Comment {comment_number} from "
                             f"{cls.auth_user.username} to post {post.id}")
                Comment.objects.create(
                    text=post_text,
                    author=cls.auth_user,
                    post=post
                )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_namespace_and_templates(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',

            reverse('posts:group_list',
                    args=(PostsPagesTests.test_group.slug,)):
                        'posts/group_list.html',

            reverse('posts:profile',
                    args=(PostsPagesTests.auth_user.username,)):
                        'posts/profile.html',

            reverse('posts:post_detail',
                    args=(PostsPagesTests.test_post.id,)):
                        'posts/post_detail.html',

            reverse('posts:post_edit',
                    args=(PostsPagesTests.test_post.id,)):
                        'posts/create_post.html',

            reverse('posts:post_create'): 'posts/create_post.html',
        }

        check_responses_of_given_urls(self,
                                      PostsPagesTests.auth_client,
                                      check_template,
                                      templates_pages_names)

    def test_create_edit_post_context(self):
        test_urls = [
            reverse("posts:post_create"),
            reverse("posts:post_edit",
                    args=(PostsPagesTests.test_post.id,))
        ]

        form_fields = {
            "text": forms.CharField,
            "group": forms.ChoiceField,
            "image": forms.ImageField
        }

        for url in test_urls:
            with self.subTest(url=url):
                response = PostsPagesTests.auth_client.get(url)
                check_form_fields_type(self,
                                       response.context['form'],
                                       form_fields)

    def test_post_detail_context_for_auth_client(self):
        # Check post content
        response = PostsPagesTests.auth_client.get(
            reverse(
                "posts:post_detail",
                args=(PostsPagesTests.test_post.id,)))

        check_posts_fields(self,
                           [response.context.get("post")],
                           [PostsPagesTests.test_post])

        # Check comment form
        self.assertIsInstance(response.context["form"], CommentForm)

        comment_form_fields_types = {
            "text": forms.CharField
        }
        check_form_fields_type(self,
                               response.context["form"],
                               comment_form_fields_types)

    def test_post_detail_context_for_unauth_client(self):
        # Check post content
        response = PostsPagesTests.guest_client.get(
            reverse(
                "posts:post_detail",
                args=(PostsPagesTests.test_post.id,)))

        check_posts_fields(self,
                           [response.context.get("post")],
                           [PostsPagesTests.test_post])

        # Check page dont contain comment form
        self.assertNotIn("form", response.context)

    def test_index_page_context_and_paginator(self):
        POSTS_PER_PAGE = 10
        response = PostsPagesTests.auth_client.get(reverse("posts:index"))
        posts_from_page = response.context.get("page_obj")
        database_posts = Post.objects.all()[:POSTS_PER_PAGE]

        check_posts_fields(self, posts_from_page, database_posts)

    def test_profile_page_context_and_paginator(self):
        POSTS_PER_PAGE = 10
        for author in PostsPagesTests.tests_authors:
            with self.subTest(author=author):
                response = PostsPagesTests.auth_client.get(
                    reverse(
                        "posts:profile",
                        args=(author.username,)))
                posts_from_page = response.context.get("page_obj")
                posts_from_database = (Post
                                       .objects
                                       .filter(author=author)
                                       [:POSTS_PER_PAGE])
                check_posts_fields(self, posts_from_page, posts_from_database)

    def test_group_page_context_and_paginator(self):
        POSTS_PER_PAGE = 10
        for group in PostsPagesTests.tests_groups:
            with self.subTest(group=group):
                response = PostsPagesTests.auth_client.get(
                    reverse(
                        "posts:group_list",
                        args=(group.slug,)))
                posts_from_page = response.context.get("page_obj")
                posts_from_database = (Post
                                       .objects
                                       .filter(group=group)
                                       [:POSTS_PER_PAGE])
                check_posts_fields(self, posts_from_page, posts_from_database)

    def test_new_post_creation(self):
        new_post_with_group = Post.objects.create(
            text="new_post",
            group=PostsPagesTests.test_group,
            author=PostsPagesTests.auth_user,
            image=create_image()
        )

        # 1 Checking pages that should contain new_post
        urls_to_check_with_new_post = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    args=(PostsPagesTests.test_group.slug,)),
            reverse('posts:profile',
                    args=(PostsPagesTests.auth_user.username,))
        ]
        for url in urls_to_check_with_new_post:
            with self.subTest(url=url):
                posts_from_page = (PostsPagesTests.
                                   auth_client
                                   .get(url)
                                   .context['page_obj']).object_list
                check_page_contains_post_on_first_position(self,
                                                           posts_from_page,
                                                           new_post_with_group)

        # 2 Checking pages that should not contain new_post
        profile_urls_to_check = ([
                                 reverse('posts:profile',
                                         args=(user.username,))
                                 for user in PostsPagesTests.tests_authors])

        group_urls_to_check = ([
                               reverse('posts:group_list',
                                       args=(group.slug,))
                               for group in PostsPagesTests.tests_groups])

        all_urls_to_check = profile_urls_to_check + group_urls_to_check

        for url in all_urls_to_check:
            with self.subTest(url=url):
                response = PostsPagesTests.auth_client.get(url)
                page_posts = response.context['page_obj']  # type:Page
                wrong_posts_count = sum(
                    post.id == new_post_with_group.id for post in page_posts)
                self.assertEquals(wrong_posts_count, 0)

    def test_profile_page_contains_all_comments(self):
        for post in Post.objects.all():
            with self.subTest(post=post):
                response = (PostsPagesTests.
                            auth_client.
                            get(
                                reverse('posts:post_detail',
                                        args=(post.pk,))))

                comments = response.context['comments']
                last_comment_in_base = Comment.objects.filter(post=post).all()
                compare_model_objects_list(self,
                                           comments,
                                           last_comment_in_base)
