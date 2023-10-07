from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from tests.core.factories.images import AppImageObjectFactory
from tests.widgets.factories.widgets import WidgetAppFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widget_app_by_id_as_partner_employee(employee_api_client, owner, partner):
    """Test get widget app by id as partner employee."""

    # When
    image_object = AppImageObjectFactory.create(owner=owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # Expected 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert len(response_dict) == 6

    assert response_dict["partner"] == str(widget_app.partner.id)
    assert response_dict["name"] == widget_app.name
    assert response_dict["link"] == widget_app.link
    assert "created_at" in response_dict

    assert len(response_dict["image"]) == 6
    retrieved_image = response_dict["image"]

    assert retrieved_image["id"] == str(image_object.id)
    assert retrieved_image["owner"] == str(image_object.owner.id)
    assert retrieved_image["name"] == image_object.name
    assert "image" in retrieved_image["image"]
    assert "file_size" in retrieved_image
    assert "created_at" in retrieved_image


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widget_app_as_partner_employee(employee_api_client, owner, partner):
    """Test list widget apps as partner employee."""

    # When
    image_object = AppImageObjectFactory.create(owner=partner.owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)
    WidgetAppFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # Expected 201 OK
    assert response.status_code == status.HTTP_200_OK
    assert len(response_dict) == 4

    assert "next" in response_dict
    assert "previous" in response_dict
    assert response_dict["count"] == 2

    assert len(response_dict["results"]) == 2
    first_widget_app = response_dict["results"][-1]

    assert first_widget_app["partner"] == str(widget_app.partner.id)
    assert first_widget_app["name"] == widget_app.name
    assert first_widget_app["link"] == widget_app.link
    assert "created_at" in first_widget_app

    assert len(first_widget_app["image"]) == 6
    retrieved_image = first_widget_app["image"]

    assert retrieved_image["id"] == str(image_object.id)
    assert retrieved_image["owner"] == str(image_object.owner.id)
    assert retrieved_image["name"] == image_object.name
    assert "image" in retrieved_image["image"]
    assert "file_size" in retrieved_image
    assert "created_at" in retrieved_image
