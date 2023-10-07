from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from tests.core.factories.images import BannerImageObjectFactory
from tests.widgets.factories.widgets import BannerFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_banner_by_id_as_partner_employee(employee_api_client, owner, partner):
    """Test get banner by id as partner employee."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    # Then
    response = employee_api_client.get(endpoint)

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
def test_get_banners_as_partner_employee(employee_api_client, owner, partner):
    """Test list banners as partner employee."""

    # When
    image_object = BannerImageObjectFactory.create(owner=owner)

    banner = BannerFactory(partner=partner, image=image_object)
    BannerFactory(partner=partner, image=image_object)

    endpoint = reverse("api-root:banners-list")

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
