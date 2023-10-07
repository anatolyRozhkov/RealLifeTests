import uuid
from unittest.mock import Mock, patch

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Banner
from tests.core.factories.images import BannerImageObjectFactory
from tests.roles.factories.partners import PartnerFactory
from tests.widgets.factories.widgets import BannerDictFactory, BannerFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_banner_as_partner_owner(owner_api_client, owner, partner):
    """Create banner as partner owner"""

    # When
    # Create image for payload
    image_object = BannerImageObjectFactory.create(owner=owner)

    # Create payload
    data = BannerDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:banners-list")

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

    assert Banner.objects.filter(id=response_dict["id"]).exists()


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_banner_by_id_as_partner_owner(owner_api_client, partner, owner):
    """Test get banner by id as partner owner."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    # Then
    response = owner_api_client.get(endpoint)

    response_dict = response.json()

    # Expected 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert len(response_dict) == 6

    assert response_dict["partner"] == str(banner.partner.id)
    assert response_dict["name"] == banner.name
    assert response_dict["link"] == banner.link
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
def test_get_banners_as_partner_owner(owner_api_client, owner, partner):
    """Test list banners as partner owner."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory.create(partner=partner, image=image_object)
    BannerFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:banners-list")

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
    first_banner = response_dict["results"][-1]

    assert first_banner["partner"] == str(banner.partner.id)
    assert first_banner["name"] == banner.name
    assert first_banner["link"] == banner.link
    assert "created_at" in first_banner

    assert len(first_banner["image"]) == 6
    retrieved_image = first_banner["image"]

    assert retrieved_image["id"] == str(image_object.id)
    assert retrieved_image["owner"] == str(image_object.owner.id)
    assert retrieved_image["name"] == image_object.name
    assert "image" in retrieved_image["image"]
    assert "file_size" in retrieved_image
    assert "created_at" in retrieved_image


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_put_banner_as_partner_owner(owner_api_client, owner, partner):
    """Test update banner as partner owner."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory.create(partner=partner, image=image_object)

    # Create new data for update payload
    new_image_object = BannerImageObjectFactory.create(owner=owner)
    new_partner = PartnerFactory.create()

    # Create update payload
    data = BannerDictFactory.build(
        # This should be updated
        image=str(new_image_object.id),
        name=Faker("name"),
        link=f"https://{uuid.uuid4()}.com",
        # This should not be updated
        partner=str(new_partner.id),
    )

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_banner = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_banner.delay", mock_send_fcm_to_devices_by_given_banner
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
        mock_send_fcm_to_devices_by_given_banner.assert_called_once_with(banner.id)


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_patch_banner_as_partner_owner(owner_api_client, owner, partner):
    """Test partially update banner as partner owner."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory(partner=partner, image=image_object)

    # Create new data for update payload
    new_image_object = BannerImageObjectFactory.create(owner=owner)
    new_partner = PartnerFactory.create()

    # Create update payload
    data = BannerDictFactory.build(
        # This should be updated
        image=str(new_image_object.id),
        name=Faker("name"),
        link=f"https://{uuid.uuid4()}.com",
        # This should not be updated
        partner=str(new_partner.id),
    )

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_banner = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_banner.delay", mock_send_fcm_to_devices_by_given_banner
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
        mock_send_fcm_to_devices_by_given_banner.assert_called_once_with(banner.id)


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_delete_banner_as_partner_owner(owner_api_client, owner, partner):
    """Test destroy banner as partner owner."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    # Then
    response = owner_api_client.delete(endpoint)

    # Expected 200 NO CONTENT
    assert response.status_code == status.HTTP_204_NO_CONTENT
