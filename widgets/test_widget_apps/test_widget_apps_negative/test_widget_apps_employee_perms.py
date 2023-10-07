from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import WidgetApp
from tests.core.factories.images import AppImageObjectFactory
from tests.widgets.factories.widgets import WidgetAppDictFactory, WidgetAppFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["delete", "patch", "put"])
def test_make_forbidden_requests_to_widget_apps_by_id_as_partner_employee(
    http_method, employee_api_client, owner, partner
):
    """Test put, patch, delete widget apps by id as partner employee."""

    # When
    # Create image
    image_object = AppImageObjectFactory.create(owner=owner)

    # Create widget app
    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    http_client_method = getattr(employee_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_app_as_partner_employee(employee_api_client, employee, partner):
    """Test post widget app as partner employee."""

    # When
    # Create image
    image_object = AppImageObjectFactory.create(owner=employee)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = employee_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widget_app_by_id_as_partner_employee_without_widget_app_ownership(employee_api_client):
    """Test get widget app by id as partner employee without widget app ownership."""

    # When
    # Create widget_app that is unrelated to the current employee
    widget_app = WidgetAppFactory.create()

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # Expected 404 NOT FOUND
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_dict["errors"]["non_field_errors"][0] == "Страница не найдена."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widget_apps_as_partner_employee_without_widget_app_ownership(employee_api_client):
    """Test listing widget apps as partner employee without widget apps' ownership."""

    # When
    # Create widget app that is unrelated to the current employee
    WidgetAppFactory.create()

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # Count num of widget apps in total
    num_of_widget_apps = WidgetApp.objects.count()

    # Expected 200 OK
    assert response.status_code == status.HTTP_200_OK

    assert num_of_widget_apps == 1
    assert len(response_dict["results"]) == 0
