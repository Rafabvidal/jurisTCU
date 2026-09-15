import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()
