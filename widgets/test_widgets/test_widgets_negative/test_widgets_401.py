import uuid

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "post"])
def test_make_requests_to_widgets_as_unauthorized_user(client, http_method):
    """Test requests to widgets as an unauthorized user."""

    # When
    endpoint = reverse("api-root:widgets-list")

    http_client_method = getattr(client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_dict["errors"]["non_field_errors"][0] == "Учетные данные не были предоставлены."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "put", "patch", "delete"])
def test_make_requests_to_widgets_id_as_unauthorized_user(client, http_method):
    """Test retrieving, updating, and partially updating widgets as an unauthorized user."""

    # When
    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": uuid.uuid4()})

    http_client_method = getattr(client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_dict["errors"]["non_field_errors"][0] == "Учетные данные не были предоставлены."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("target_for_removal", ["banners", "widget-apps"])
def test_delete_widget_banners_and_widget_apps_as_an_unauthorized_user(target_for_removal, client):
    """Test deleting banners, widget apps from a widget object as an unauthorized user."""

    # When
    endpoint = reverse(f"api-root:widgets-remove-{target_for_removal}", kwargs={"pk": uuid.uuid4()})

    # Then
    response = client.delete(endpoint + f"?ids={uuid.uuid4()}")

    response_dict = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_dict["errors"]["non_field_errors"][0] == "Учетные данные не были предоставлены."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_in_csv_as_an_unauthorized_user(client):
    """
    Test downloading csv file with widgets as an unauthorized user.
    """

    # When
    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = client.get(endpoint)

    response_dict = response.json()

    # response should be 401 UNAUTHORIZED
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_dict["errors"]["non_field_errors"][0] == "Учетные данные не были предоставлены."
