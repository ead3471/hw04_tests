from django.test import TestCase
from typing import Iterable
from django.utils.crypto import get_random_string
from django.db.models import Max
from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.core.paginator import Page

User = get_user_model()


def check_posts_fields(test_case: TestCase,
                       posts_from_page: Iterable,
                       expected_posts: Iterable):
    """Sequentely compares all the post objects from
    posts_from_page with posts from expected_posts"""

    posts_attributes = [
        "text",
        "group",
        "pub_date",
        "author"
    ]
    test_case.assertEquals(len(posts_from_page), len(expected_posts))
    for post_from_page, expected_post in zip(posts_from_page,
                                             expected_posts):
        with test_case.subTest(post_from_page=post_from_page,
                               expected_post=expected_post):
            for attribute in posts_attributes:
                with test_case.subTest(attribute=attribute):
                    test_case.assertEquals(
                        post_from_page.__getattribute__(attribute),
                        expected_post.__getattribute__(attribute))


def check_page_contains_post_on_first_position(test_case: TestCase,
                                               posts: Page,
                                               expected_post: Post):
    test_case.assertGreater(len(posts), 0)
    test_case.assertEquals(posts[0].id, expected_post.id)


def get_not_used_group_slug() -> str:
    random_slug = get_random_string(7)
    while random_slug in Group.objects.values_list("slug"):
        random_slug = get_random_string(7)
    return random_slug


def get_not_used_post_id() -> int:
    return Post.objects.all().aggregate(Max("id"))["id__max"] + 1


def get_not_used_username() -> str:
    random_username = get_random_string(7)
    while random_username in User.objects.values_list("username"):
        random_username = get_random_string(7)
    return random_username
