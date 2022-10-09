from django.test import TestCase
from typing import Iterable


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
