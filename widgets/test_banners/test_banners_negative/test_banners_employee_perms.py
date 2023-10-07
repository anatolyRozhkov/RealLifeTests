from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Banner
from tests.core.factories.images import BannerImageObjectFactory
from tests.widgets.factories.widgets import BannerDictFactory, BannerFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["delete", "patch", "put"])
def test_make_forbidden_requests_to_banners_by_id_as_partner_employee(http_method, employee_api_client, owner, partner):
    """Test put, patch, delete banners by id as partner employee."""

    # When
    # Create image
    image_object = BannerImageObjectFactory.create(owner=owner)

    # Create banner
    banner = BannerFactory.create(partner=partner, image=image_object)

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    http_client_method = getattr(employee_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    # Expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_banner_as_partner_employee(employee_api_client, employee, partner):
    """Test post banner as partner employee."""

    # When
    # Create image
    image_object = BannerImageObjectFactory.create(owner=employee)

    # Create payload
    data = BannerDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:banners-list")

    # Then
    response = employee_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 403 FORBIDDEN
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response_dict["errors"]["non_field_errors"][0] == "У вас недостаточно прав для выполнения данного действия."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_banner_by_id_as_partner_employee_without_banner_ownership(employee_api_client):
    """Test get banner by id as partner employee without banner ownership."""

    # When
    # Create banner that is unrelated to the current employee
    banner = BannerFactory.create()

    endpoint = reverse("api-root:banners-detail", kwargs={"pk": banner.id})

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # Expected 404 NOT FOUND
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_dict["errors"]["non_field_errors"][0] == "Страница не найдена."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_banners_as_partner_employee_without_banners_ownership(employee_api_client):
    """Test listing banners as partner employee without banners' ownership."""

    # When
    # Create banner that is unrelated to the current employee
    BannerFactory.create()

    endpoint = reverse("api-root:banners-list")

    # Then
    response = employee_api_client.get(endpoint)

    response_dict = response.json()

    # Count num of banners in total
    num_of_banners = Banner.objects.count()

    # Expected 200 OK
    assert response.status_code == status.HTTP_200_OK

    assert num_of_banners == 1
    assert len(response_dict["results"]) == 0
