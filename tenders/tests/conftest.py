import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def user():
    """Create test user"""

    user_model = get_user_model()

    return user_model.objects.create_user(
        username="testuser",
        password="testpassword",
    )


@pytest.fixture
def api_client():
    """Create API client"""

    return APIClient()
