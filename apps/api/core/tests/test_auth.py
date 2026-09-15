from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token

from core.tests.base import BaseAPITestCase
from core.tests.helpers import DataSetup

REGISTER_ENDPOINT = "/api/auth/register/"
LOGIN_ENDPOINT = "/api/auth/login/"
LOGOUT_ENDPOINT = "/api/auth/logout/"
ME_ENDPOINT = "/api/auth/me/"


class TestRegister(BaseAPITestCase):
    def test_given_valid_payload_when_register_then_creates_user_and_returns_token(self) -> None:
        payload = {"name": "Beatriz", "email": "Beatriz@Example.com", "password": "uma-senha-forte-123"}

        response = self.client.post(REGISTER_ENDPOINT, payload, format="json")

        self.assert_response_success(response, status.HTTP_201_CREATED)
        data = response.json()
        self.assertTrue(data.get("token"))
        self.assertEqual(data["user"]["email"], "beatriz@example.com")
        self.assertEqual(data["user"]["name"], "Beatriz")

        # username e email sao gravados normalizados (lowercase) e o token persiste.
        user = User.objects.get(email="beatriz@example.com")
        self.assertEqual(user.username, "beatriz@example.com")
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_given_duplicate_email_when_register_then_returns_400(self) -> None:
        DataSetup.create_user(email="taken@example.com", password="abc12345xyz")  # noqa: S106
        payload = {"email": "taken@example.com", "password": "outra-senha-456"}

        response = self.client.post(REGISTER_ENDPOINT, payload, format="json")

        self.assert_response_fail(response, status.HTTP_400_BAD_REQUEST, "email")

    def test_given_weak_password_when_register_then_returns_400(self) -> None:
        payload = {"email": "novo@example.com", "password": "123"}

        response = self.client.post(REGISTER_ENDPOINT, payload, format="json")

        self.assert_response_fail(response, status.HTTP_400_BAD_REQUEST, "password")


class TestLogin(BaseAPITestCase):
    def test_given_valid_credentials_when_login_then_returns_token(self) -> None:
        DataSetup.create_user(email="ana@example.com", password="senha-correta-789")  # noqa: S106
        payload = {"email": "ana@example.com", "password": "senha-correta-789"}

        response = self.client.post(LOGIN_ENDPOINT, payload, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertTrue(response.json().get("token"))

    def test_given_wrong_password_when_login_then_returns_401(self) -> None:
        DataSetup.create_user(email="ana@example.com", password="senha-correta-789")  # noqa: S106
        payload = {"email": "ana@example.com", "password": "senha-errada"}

        response = self.client.post(LOGIN_ENDPOINT, payload, format="json")

        self.assert_response_unauthorized(response)


class TestUserMeAndLogout(BaseAPITestCase):
    def _auth_user(self, email: str = "user@example.com", password: str = "senha-do-user-321") -> Token:  # noqa: S107
        user = DataSetup.create_user(email=email, password=password, name="User")
        token = DataSetup.create_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return token

    def test_given_no_token_when_get_me_then_returns_401(self) -> None:
        response = self.client.get(ME_ENDPOINT)
        self.assert_response_unauthorized(response)

    def test_given_token_when_get_me_then_returns_profile(self) -> None:
        self._auth_user()

        response = self.client.get(ME_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "user@example.com")

    def test_given_token_when_patch_me_then_updates_profile_name(self) -> None:
        token = self._auth_user()

        response = self.client.patch(ME_ENDPOINT, {"name": "New Name"})

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "New Name")

        # Verify database update
        token.user.refresh_from_db()
        self.assertEqual(token.user.first_name, "New Name")

    def test_given_token_when_logout_then_revokes_token(self) -> None:
        token = self._auth_user()

        response = self.client.post(LOGOUT_ENDPOINT)

        self.assert_response_success(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(key=token.key).exists())
