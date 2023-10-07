import uuid

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "post"])
def test_make_requests_to_widget_apps_as_user(http_method, user_api_client):
    """Test make post and get requests to widget apps as a user."""

    # When
    endpoint = reverse("api-root:widget_apps-list")

    http_client_method = getattr(user_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "put", "patch", "delete"])
def test_make_requests_to_widget_apps_by_id_a_user(http_method, user_api_client):
    """Test make get, put, patch, delete requests to widget apps by id as a user."""

    # When
    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": uuid.uuid4()})

    http_client_method = getattr(user_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."
