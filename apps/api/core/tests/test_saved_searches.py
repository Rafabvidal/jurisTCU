from rest_framework import status

from core.models.busca_salva import BuscaSalva
from core.tests.base import BaseAPITestCase
from core.tests.helpers import DataSetup

SAVED_SEARCHES_ENDPOINT = "/api/saved-searches/"


class TestSavedSearchesPermissions(BaseAPITestCase):
    def test_given_no_token_when_list_then_returns_401(self) -> None:
        response = self.client.get(SAVED_SEARCHES_ENDPOINT)
        self.assert_response_unauthorized(response)

    def test_given_no_token_when_create_then_returns_401(self) -> None:
        response = self.client.post(
            SAVED_SEARCHES_ENDPOINT, {"title": "x", "query": "y"}, format="json"
        )
        self.assert_response_unauthorized(response)


class TestSavedSearchesCrud(BaseAPITestCase):
    def test_given_authenticated_user_when_create_then_associates_to_user(self) -> None:
        user = DataSetup.create_user(email="dono@example.com")
        token = DataSetup.create_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.post(
            SAVED_SEARCHES_ENDPOINT,
            {"title": "Escala 12x36", "query": "trabalhei 12h sem intervalo"},
            format="json",
        )

        self.assert_response_success(response, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["title"], "Escala 12x36")

        busca = BuscaSalva.objects.get(id=data["id"])
        self.assertEqual(busca.user.email, "dono@example.com")

    def test_given_searches_from_two_users_when_list_then_returns_only_own(self) -> None:
        user_a = DataSetup.create_user(email="a@example.com")
        token_a = DataSetup.create_token(user_a)

        user_b = DataSetup.create_user(email="b@example.com")
        DataSetup.create_token(user_b)

        # Create saved searches via data factory
        DataSetup.create_busca_salva(user_a, title="A", query="qa")
        DataSetup.create_busca_salva(user_b, title="B", query="qb")

        # Authenticate client as user_a
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token_a.key}")
        response = self.client.get(SAVED_SEARCHES_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        titles = [item["title"] for item in response.json()["results"]]
        self.assertEqual(titles, ["A"])

    def test_given_owned_search_when_delete_then_removes_it(self) -> None:
        user = DataSetup.create_user(email="dono@example.com")
        token = DataSetup.create_token(user)
        busca = DataSetup.create_busca_salva(user, title="Apagar", query="q")

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.delete(f"{SAVED_SEARCHES_ENDPOINT}{busca.id}/")

        self.assert_response_success(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BuscaSalva.objects.filter(id=busca.id).exists())

    def test_given_other_users_search_when_delete_then_returns_404(self) -> None:
        user_a = DataSetup.create_user(email="a@example.com")
        busca = DataSetup.create_busca_salva(user_a, title="A", query="qa")

        user_b = DataSetup.create_user(email="b@example.com")
        token_b = DataSetup.create_token(user_b)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token_b.key}")
        response = self.client.delete(f"{SAVED_SEARCHES_ENDPOINT}{busca.id}/")

        self.assert_response_not_found(response)
        self.assertTrue(BuscaSalva.objects.filter(id=busca.id).exists())
