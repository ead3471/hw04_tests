from django.test import TestCase, Client
from typing import Callable, Dict


def check_responses_with_dict_of_urls(test_case: TestCase,
                                      client: Client,
                                      response_check_function: Callable,
                                      urls_dict: Dict):
    for url, expected_value in urls_dict.items():
        with test_case.subTest(url=url, expected_value=expected_value):
            response = client.get(url)
            response_check_function(test_case, response, expected_value)


def check_status_code(test_case: TestCase, response, expected_value):
    test_case.assertEquals(response.status_code, expected_value)


def check_template(test_case: TestCase, response, expected_value):
    test_case.assertTemplateUsed(response, expected_value)
