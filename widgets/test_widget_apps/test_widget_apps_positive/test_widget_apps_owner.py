import uuid
from unittest.mock import Mock, patch

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import WidgetApp
from tests.core.factories.images import AppImageObjectFactory
from tests.roles.factories.partners import PartnerFactory
from tests.widgets.factories.widgets import WidgetAppDictFactory, WidgetAppFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_app_as_partner_owner(owner_api_client, owner, partner):
    """Create widget app as partner owner."""

    # When
    # Create image for payload
    image_object = AppImageObjectFactory.create(owner=owner)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = owner_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 201 CREATED
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response_dict) == 6

    assert response_dict["partner"] == data["partner"]
    assert response_dict["name"] == data["name"]
    assert response_dict["image"] == data["image"]
    assert response_dict["link"] == data["link"]
    assert "created_at" in response_dict

    assert WidgetApp.objects.filter(id=response_dict["id"]).exists()


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widget_app_by_id_as_partner_owner(owner_api_client, partner, owner):
    """Test get widget app by id as partner owner."""

    # When
    image_object = AppImageObjectFactory.create(owner=owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    # Then
    response = owner_api_client.get(endpoint)

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
def test_get_widget_apps_as_partner_owner(owner_api_client, partner, owner):
    """Test list widget apps as partner owner."""

    # When
    image_object = AppImageObjectFactory.create(owner=owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)
    WidgetAppFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = owner_api_client.get(endpoint)

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


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_put_widget_app_as_partner_owner(owner_api_client, partner, owner):
    """Test update widget app as partner owner."""

    # When
    image_object = AppImageObjectFactory.create(owner=owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    # Create new data for update payload
    new_image_object = AppImageObjectFactory.create(owner=owner)
    new_partner = PartnerFactory.create()

    # Create update payload
    data = WidgetAppDictFactory.build(
        # This should be updated
        image=str(new_image_object.id),
        name=Faker("name"),
        link=f"https://{uuid.uuid4()}.com",
        # This should not be updated
        partner=str(new_partner.id),
    )

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_widget_application = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_widget_application.delay",
        mock_send_fcm_to_devices_by_given_widget_application,
    ):
        response = owner_api_client.put(endpoint, data=data)

        response_dict = response.json()

        # Expected 200 OK
        assert response.status_code == status.HTTP_200_OK

        assert len(response_dict) == 6

        assert response_dict["partner"] == str(partner.id)
        assert response_dict["name"] == data["name"]
        assert response_dict["image"] == data["image"]
        assert response_dict["link"] == data["link"]
        assert "created_at" in response_dict

        # Assert that the Celery tasks were called with the expected arguments
        mock_send_fcm_to_devices_by_given_widget_application.assert_called_once_with(widget_app.id)


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_patch_widget_app_as_partner_owner(owner_api_client, partner, owner):
    """Test partially update widget app as partner owner."""

    # When
    image_object = AppImageObjectFactory.create(owner=owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    # Create new data for update payload
    new_image_object = AppImageObjectFactory.create(owner=owner)
    new_partner = PartnerFactory.create()

    # Create update payload
    data = WidgetAppDictFactory.build(
        # This should be updated
        image=str(new_image_object.id),
        name=Faker("name"),
        link=f"https://{uuid.uuid4()}.com",
        # This should not be updated
        partner=str(new_partner.id),
    )

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_widget_application = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_widget_application.delay",
        mock_send_fcm_to_devices_by_given_widget_application,
    ):
        response = owner_api_client.patch(endpoint, data=data)

        response_dict = response.json()

        # Expected 200 OK
        assert response.status_code == status.HTTP_200_OK

        assert len(response_dict) == 6

        assert response_dict["partner"] == str(partner.id)
        assert response_dict["name"] == data["name"]
        assert response_dict["image"] == data["image"]
        assert response_dict["link"] == data["link"]
        assert "created_at" in response_dict

        # Assert that the Celery tasks were called with the expected arguments
        mock_send_fcm_to_devices_by_given_widget_application.assert_called_once_with(widget_app.id)


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_delete_widget_app_as_partner_owner(owner_api_client, owner, partner):
    """Test destroy widget app as partner owner."""

    # When
    image_object = AppImageObjectFactory.create(owner=owner)

    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    # Then
    response = owner_api_client.delete(endpoint)

    # Expected 200 NO CONTENT
    assert response.status_code == status.HTTP_204_NO_CONTENT
