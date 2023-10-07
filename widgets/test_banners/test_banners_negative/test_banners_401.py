import uuid

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "post"])
def test_make_requests_to_banners_as_unauthorized_user(http_method, client):
    """Test make post and get requests to banners as an unauthorised user."""

    # When
    endpoint = reverse("api-root:banners-list")

    http_client_method = getattr(client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 401 UNAUTHORIZED
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_dict["errors"]["non_field_errors"][0] == "Учетные данные не были предоставлены."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "put", "patch", "delete"])
def test_make_requests_to_banners_by_id_as_unauthorized_user(http_method, client):
    """Test make get, put, patch, delete requests to banners by id as an
    unauthorized user."""

    # When
    endpoint = reverse("api-root:triggers-detail", kwargs={"pk": uuid.uuid4()})

    http_client_method = getattr(client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 401 UNAUTHORIZED
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_dict["errors"]["non_field_errors"][0] == "Учетные данные не были предоставлены."
