from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase

from core.tests.constants import DEDUPLICAR_ENDPOINT


class APITestAssertionsMixin:
    def assert_response_success(self, response: Response | HttpResponse, expected_status: int | None = None) -> None:
        """Asserts response status code is a 2xx success (and matches expected_status if provided)."""
        is_success = 200 <= response.status_code < 300
        self.assertTrue(
            is_success,
            f"Expected successful response (2xx), got status code {response.status_code}. "
            f"Response: {response.content.decode('utf-8', errors='ignore')}"
        )
        if expected_status is not None:
            self.assertEqual(
                response.status_code,
                expected_status,
                f"Expected status code {expected_status}, got {response.status_code}."
            )

    def assert_response_fail(
        self,
        response: Response | HttpResponse,
        expected_status: int | None = None,
        expected_error_key: str | None = None
    ) -> None:
        """Asserts response status code is a 4xx client error or 5xx server error."""
        is_failure = 400 <= response.status_code < 600
        self.assertTrue(
            is_failure,
            f"Expected failure response (4xx/5xx), got status code {response.status_code}. "
            f"Response: {response.content.decode('utf-8', errors='ignore')}"
        )
        if expected_status is not None:
            self.assertEqual(
                response.status_code,
                expected_status,
                f"Expected status code {expected_status}, got {response.status_code}."
            )
        if expected_error_key is not None:
            try:
                data = response.json()
            except ValueError:
                self.fail(
                    f"Expected JSON response with key '{expected_error_key}', "
                    f"but content is not valid JSON: {response.content}"
                )

            if isinstance(data, dict):
                self.assertIn(
                    expected_error_key,
                    data,
                    f"Expected error key '{expected_error_key}' in response dictionary. Response: {data}"
                )
            elif isinstance(data, list):
                found = False
                for item in data:
                    if isinstance(item, dict) and expected_error_key in item:
                        found = True
                        break
                    elif isinstance(item, str) and expected_error_key in item:
                        found = True
                        break
                self.assertTrue(
                    found,
                    f"Expected error key '{expected_error_key}' in response list. Response: {data}"
                )
            else:
                self.assertEqual(
                    str(data),
                    expected_error_key,
                    f"Expected error key '{expected_error_key}' but got: {data}"
                )

    def assert_response_not_found(self, response: Response | HttpResponse) -> None:
        """Asserts response status code is 404 Not Found."""
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Expected 404 Not Found, got {response.status_code}. "
            f"Response: {response.content.decode('utf-8', errors='ignore')}"
        )

    def assert_response_unauthorized(self, response: Response | HttpResponse) -> None:
        """Asserts response status code is 401 Unauthorized."""
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f"Expected 401 Unauthorized, got {response.status_code}. "
            f"Response: {response.content.decode('utf-8', errors='ignore')}"
        )


class BaseAPITestCase(APITestAssertionsMixin, APITestCase):
    """Base API Test Case standardizing assertions and using DRF APITestCase."""
    pass


class BaseProcessoViewsetTests(BaseAPITestCase):
    endpoint: str = DEDUPLICAR_ENDPOINT

    def make_api_client(self) -> APIClient:
        return APIClient()

    def post_deduplicar(self, api_client: APIClient, payload: list[dict]):
        return api_client.post(self.endpoint, payload, format="json")
