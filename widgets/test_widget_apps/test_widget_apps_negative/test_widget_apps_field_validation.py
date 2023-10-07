from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory, ImageObjectFactory
from tests.widgets.factories.widgets import WidgetAppDictFactory, WidgetAppFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_app_with_jpg_image_format(owner_api_client, partner, owner):
    """Test post widget_app with jpg image format."""

    # When
    # Create image with jpg format
    image_object = ImageObjectFactory.create(owner=owner)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = owner_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response_dict["errors"]["image"][0] == "Расширение файлов “jpg” не поддерживается. Разрешенные расширения: png."
    )


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_app_with_incorrect_image_dimensions(owner_api_client, partner, owner):
    """Test post widget app with incorrect image dimensions."""

    # When
    # Create image with incorrect dimensions
    image_object = BannerImageObjectFactory.create(owner=owner)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(image_object.id))

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = owner_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_dict["errors"]["image"][0] == "Размер изображения должен быть равен 512x512px."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["patch", "put"])
def test_put_patch_widget_app_with_jpg_image_format(http_method, owner_api_client, partner, owner):
    """Test put, patch widget app with jpg image format."""

    # When
    # Create correct image object
    image_object = AppImageObjectFactory.create(owner=owner)

    # Create widget app to be updated
    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    # Create new image with jpg format
    new_image_object = ImageObjectFactory.create(owner=owner)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(new_image_object.id))

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    http_client_method = getattr(owner_api_client, http_method)

    # Then
    response = http_client_method(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response_dict["errors"]["image"][0] == "Расширение файлов “jpg” не поддерживается. Разрешенные расширения: png."
    )


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["patch", "put"])
def test_put_patch_widget_app_with_incorrect_image_dimensions(http_method, owner_api_client, partner, owner):
    """Test put, patch widget_app with incorrect image dimensions."""

    # When
    # Create correct image object
    image_object = AppImageObjectFactory.create(owner=owner)

    # Create widget app to be updated
    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    # Create new image with incorrect format
    new_image_object = BannerImageObjectFactory.create(owner=owner)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(new_image_object.id))

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    http_client_method = getattr(owner_api_client, http_method)

    # Then
    response = http_client_method(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_dict["errors"]["image"][0] == "Размер изображения должен быть равен 512x512px."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_app_with_invalid_link_format(owner_api_client, owner, partner):
    """Test post widget app with invalid link format."""

    # When
    # Create image object
    image_object = AppImageObjectFactory.create(owner=owner)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(image_object.id), link="some_text")

    endpoint = reverse("api-root:widget_apps-list")

    # Then
    response = owner_api_client.post(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_dict["errors"]["link"][0] == "Введите правильный URL."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["patch", "put"])
def test_put_patch_widget_app_with_invalid_link_format(http_method, owner_api_client, owner, partner):
    """Test put, patch widget app with invalid link format."""

    # When
    # Create correct image object
    image_object = AppImageObjectFactory.create(owner=owner)

    # Create widget app to be updated
    widget_app = WidgetAppFactory.create(partner=partner, image=image_object)

    # Create payload
    data = WidgetAppDictFactory.build(partner=str(partner.id), image=str(image_object.id), link="some_text")

    endpoint = reverse("api-root:widget_apps-detail", kwargs={"pk": widget_app.id})

    http_client_method = getattr(owner_api_client, http_method)

    # Then
    response = http_client_method(endpoint, data)

    response_dict = response.json()

    # Expected 400 BAD REQUEST
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_dict["errors"]["link"][0] == "Введите правильный URL."
