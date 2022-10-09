from django.test import TestCase, Client
from typing import Callable, Dict, Iterable


def check_responses_of_given_urls(test_case: TestCase,
                                  client: Client,
                                  response_check_function: Callable,
                                  urls_and_expexted_values: Dict):
    """The function accepts responses from the given urls
       and checks if they match the expected values
       by the given responce_check_function """

    for url, expected_value in urls_and_expexted_values.items():
        with test_case.subTest(url=url, expected_value=expected_value):
            response = client.get(url)
            response_check_function(test_case, response, expected_value)


def check_status_code(test_case: TestCase, response, expected_value):
    test_case.assertEquals(response.status_code, expected_value)


def check_template(test_case: TestCase, response, expected_value):
    test_case.assertTemplateUsed(response, expected_value)


def check_redirect(test_case: TestCase, response, expected_value):
    test_case.assertRedirects(response, expected_value)


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
