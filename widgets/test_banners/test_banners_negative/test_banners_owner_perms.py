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
def test_post_banners_as_owner_without_image_ownership(owner_api_client, partner):
    """Test post banner as a partner owner without owning the image."""

    # When
    # Create image that is unrelated to partner
    image_object = BannerImageObjectFactory.create()

    # Create payload
    data = BannerDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:banners-list")

    # Then
    response = owner_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response_dict["errors"]["image"][0]
        == f'Недопустимый первичный ключ "{str(image_object.id)}" - объект не существует.'
    )


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_banners_as_owner_with_unrelated_partner(owner_api_client, owner):
    """Test post banner as a partner owner with an unrelated partner."""

    # When
    # Create a new partner that is unrelated to the current one
    new_partner = PartnerFactory.create()

    # Create image
    image_object = BannerImageObjectFactory.create(owner=owner)

    # Create payload
    data = BannerDictFactory.build(partner=str(new_partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:banners-list")

    # Then
    response = owner_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response_dict["errors"]["partner"][0]
        == f'Недопустимый первичный ключ "{str(new_partner.id)}" - объект не существует.'
    )


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_banners_as_partner_owner_without_owning_them(owner_api_client):
    """Test list banners as partner owner without owning them."""

    # When
    # Create banner that partner does not own
    BannerFactory.create()

    endpoint = reverse("api-root:banners-list")

    # Then
    response = owner_api_client.get(endpoint)

    response_dict = response.json()

    number_of_banners = Banner.objects.count()

    # Expected 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert number_of_banners == 1
    assert len(response_dict["results"]) == 0


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "delete", "patch", "put"])
def test_make_requests_to_banners_by_id_as_partner_owner_without_banner_ownership(http_method, owner_api_client):
    """Test get, put, patch, delete banners by id as partner owner without banner ownership."""

    # When
    # Create banner that is not owned by the current partner
    banner = BannerFactory.create()

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    http_client_method = getattr(owner_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 404 NOT FOUND
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_dict["errors"]["non_field_errors"][0] == "Страница не найдена."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["put", "patch"])
def test_put_patch_banners_as_partner_owner_without_image_ownership(http_method, owner_api_client, owner, partner):
    """Test put, patch banners as partner owner without image ownership rights."""

    # When
    # Create image that belongs to current partner
    image_object = BannerImageObjectFactory.create(owner=owner)

    # Create banner belonging to current partner
    banner = BannerFactory.create(partner=partner, image=image_object)

    # Create new image that is not related to the current partner
    new_image_object = BannerImageObjectFactory.create()

    # Create payload
    data = BannerDictFactory.build(partner=str(partner.id), image=str(new_image_object.id))

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    http_client_method = getattr(owner_api_client, http_method)

    # Then
    response = http_client_method(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response_dict["errors"]["image"][0]
        == f'Недопустимый первичный ключ "{str(new_image_object.id)}" - объект не существует.'
    )
