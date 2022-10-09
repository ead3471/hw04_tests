from django.test import TestCase, Client
from typing import Callable, Dict


def check_responses_with_dict_of_urls(test_case: TestCase,
                                      client: Client,
                                      response_check_function: Callable,
                                      urls_dict: Dict):
    for url, expected_value in urls_dict.items():
        with self.subTest(url=url, expected_value=expected_value):
            response = client.get(url)
            response_check_function(response, expected_value)
