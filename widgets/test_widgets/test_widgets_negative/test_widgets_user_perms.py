import uuid

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("deletion_target", ["banners", "widget-apps"])
def test_delete_banners_and_widget_apps_as_user(deletion_target, user_api_client):
    """Test deleting banners and widget apps from a widget object as user."""

    # When
    endpoint = reverse(f"api-root:widgets-remove-{deletion_target}", kwargs={"pk": uuid.uuid4()})

    # Then
    response = user_api_client.delete(endpoint + f"?ids={uuid.uuid4()}")

    response_dict = response.json()

    # expected output 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "post"])
def test_make_requests_to_widgets_as_user(user_api_client, http_method):
    """Test making requests on widgets as user."""

    # When
    endpoint = reverse("api-root:widgets-list")

    http_client_method = getattr(user_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # expected output 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "put", "patch", "delete"])
def test_make_requests_to_widgets_id_as_user(user_api_client, http_method):
    """Test making requests on widgets id as user."""

    # When
    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": uuid.uuid4()})

    http_client_method = getattr(user_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_in_csv_as_user(user_api_client):
    """Test downloading widgets in csv format as user."""

    # When
    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = user_api_client.get(endpoint)

    response_dict = response.json()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."
