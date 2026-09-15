# JusTRT6 Testing Guidelines

This document outlines the standard structure, utilities, and assertions to be used when writing backend API tests. By adhering to these guidelines, we ensure consistent, robust, and highly readable test suites.

---

## 🏛️ Base Test Classes

All new test classes should subclass the appropriate base class rather than using bare classes:

1. **`BaseAPITestCase`** (in `core.tests.base`):
   - **When to use**: For standard API endpoints, authentication flows, or general database tests.
   - **Key Features**: Direct inheritance from `rest_framework.test.APITestCase` (which subclasses `unittest.TestCase`). Handles transactional rollback, Django database setup automatically, and loads the custom HTTP assertions mixin.
2. **`BaseProcessoViewsetTests`** (in `core.tests.base`):
   - **When to use**: Specifically for viewsets or endpoints dealing with document ingestion, deduplication, semantic searches, etc.
   - **Key Features**: Inherits from `BaseAPITestCase` and configures endpoint paths and serialization configurations out of the box.

---

## 🛠️ Centralized Data Setup Factory

Avoid manual ORM creation within tests. Always use the **`DataSetup`** factory class (defined in `core.tests.helpers`):

- **Create a User**:
  ```python
  user = DataSetup.create_user(email="custom@example.com", password="secure-password-123", name="Full Name")
  ```
- **Create an Auth Token**:
  ```python
  token = DataSetup.create_token(user)
  ```
- **Create a Saved Search**:
  ```python
  search = DataSetup.create_busca_salva(user, title="My Query", query="horas extras")
  ```
- **Create a Process**:
  ```python
  processo = DataSetup.create_processo_existente(numero_processo="00001234520255060001", data_hora_ultima_atualizacao=date.today())
  ```

---

## 🔍 Rich Custom Assertions

Instead of raw Python `assert` statements, use our custom, context-aware assertions provided by `APITestAssertionsMixin`. These provide rich failure logs containing the raw response body on failure:

### 1. `self.assert_response_success(response, expected_status=None)`
Asserts that the HTTP response code is within the 2xx success range.
- **Example**:
  ```python
  response = self.client.get(SAVED_SEARCHES_ENDPOINT)
  self.assert_response_success(response, status.HTTP_200_OK)
  ```

### 2. `self.assert_response_fail(response, expected_status=None, expected_error_key=None)`
Asserts that the response failed with a 4xx client or 5xx server status code, and optionally validates that a specific error field is present in the response payload.
- **Example**:
  ```python
  response = self.client.post(REGISTER_ENDPOINT, incomplete_payload)
  self.assert_response_fail(response, status.HTTP_400_BAD_REQUEST, expected_error_key="email")
  ```

### 3. `self.assert_response_not_found(response)`
Asserts that the response code is exactly `404 Not Found`.
- **Example**:
  ```python
  response = self.client.delete(f"{SAVED_SEARCHES_ENDPOINT}99999/")
  self.assert_response_not_found(response)
  ```

### 4. `self.assert_response_unauthorized(response)`
Asserts that the response code is exactly `401 Unauthorized`.
- **Example**:
  ```python
  response = self.client.get(ME_ENDPOINT)
  self.assert_response_unauthorized(response)
  ```

---

## 📋 Standard Testing Template

Here is a clean copy-paste template for creating a new test module:

```python
from rest_framework import status

from core.tests.base import BaseAPITestCase
from core.tests.helpers import DataSetup

ENDPOINT = "/api/my-feature/"


class TestMyFeatureEndpoints(BaseAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        # Create standard test user and authenticate client
        self.user = DataSetup.create_user(email="test@example.com")
        self.token = DataSetup.create_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_given_valid_payload_when_post_then_returns_200(self) -> None:
        payload = {"data": "my-value"}
        
        response = self.client.post(ENDPOINT, payload, format="json")
        
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json()["data"], "my-value")

    def test_given_unauthenticated_request_when_post_then_returns_401(self) -> None:
        # Clear credentials for this test
        self.client.credentials()
        
        response = self.client.post(ENDPOINT, {}, format="json")
        
        self.assert_response_unauthorized(response)
```

---

## 🚀 Running the Test Suite

Execute the API tests from the project root:
```bash
make test-api
```
Or execute a specific test file:
```bash
cd apps/api && uv run pytest core/tests/test_auth.py
```
