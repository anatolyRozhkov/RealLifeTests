import uuid

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Widget
from tests.utilities.read_csv import ReadCSV
from tests.widgets.factories.widgets import WidgetFactory

"""
Partner employee must not have permissions to post, put, patch, delete widgets
and delete banners, widget apps.
"""


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["put", "patch", "delete"])
def test_make_forbidden_requests_to_widgets_as_partner_employee(http_method, employee_api_client):
    """Test make forbidden requests to widgets as partner employee."""

    # When
    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": uuid.uuid4()})

    http_client_method = getattr(employee_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # expected output 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widgets_as_partner_employee(employee_api_client):
    """Test post widgets as partner employee."""

    # When
    endpoint = reverse("api-root:widgets-list")

    # Then
    response = employee_api_client.post(endpoint)

    response_dict = response.json()

    # expected output 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("deletion_target", ["banners", "widget-apps"])
def test_delete_banners_widget_apps_as_partner_employee(deletion_target, employee_api_client):
    """Test deleting banners and widget apps from a widget object as partner employee."""

    # When
    endpoint = reverse(f"api-root:widgets-remove-{deletion_target}", kwargs={"pk": uuid.uuid4()})

    # Then
    response = employee_api_client.delete(endpoint + f"?ids={uuid.uuid4()}")

    response_dict = response.json()

    # expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


"""
Make requests on widget objects when widget.partner is unrelated to partner employee.
"""


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_id_as_partner_employee_without_widget_ownership(employee_api_client):
    """Test retrieve widget by id when widget is unrelated to partner_employee."""

    # When
    widget = WidgetFactory.create()

    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": widget.id})

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_dict["errors"]["non_field_errors"][0] == "Страница не найдена."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_by_partner_employee_without_widget_ownership(employee_api_client):
    """Test getting widget when it is unrelated to partner employee."""
    # When
    WidgetFactory.create()

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert response_dict["count"] == 0


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_in_csv_by_partner_employee_without_widgets_ownership(employee_api_client):
    """Test getting widgets in csv format when widgets is unrelated to partner employee."""

    # When
    WidgetFactory.create()

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = employee_api_client.get(endpoint)

    # get data from csv
    extracted_data = ReadCSV(response)
    values = extracted_data.values()

    widget_objects_count = Widget.objects.count()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 1

    assert len(values) == 0
