from unittest.mock import Mock, patch

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Widget
from tests.core.factories.images import AppImageObjectFactory
from tests.roles.factories.partners import PartnerFactory
from tests.utilities.read_csv import ReadCSV
from tests.widgets.factories.widgets import BannerFactory, WidgetDictFactory, WidgetFactory

"""
Create widget object when logo.owner/partner.owner != logged-in partner owner.
"""


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_as_partner_owner_without_widget_partner_ownership(owner_api_client, owner):
    """Test creating widget when widget.partner.owner != logged-in partner owner."""

    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create partner that is not related to owner
    new_partner = PartnerFactory.create()

    # Create payload
    data = WidgetDictFactory.build(
        logo=str(app_image),
        partner=str(new_partner.id),
        banners=[],
        applications=[],
    )

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.post(endpoint, data=data)

    response_dict = response.json()

    # 400 BAS REQUEST is expected
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert (
        response_dict["errors"]["partner"][0]
        == f'Недопустимый первичный ключ "{str(new_partner.id)}" - объект не существует.'
    )


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_as_partner_owner_without_widget_logo_ownership(owner_api_client, partner):
    """Test creating widget when widget.logo.owner != logged-in partner owner."""

    # When
    # Create app image that is unrelated to the current partner
    app_image = AppImageObjectFactory.create()

    # Create payload
    data = WidgetDictFactory.build(
        logo=str(app_image.id),
        partner=str(partner.id),
        banners=[],
        applications=[],
    )

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.post(endpoint, data=data)

    response_dict = response.json()

    # 400 BAS REQUEST is expected
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert (
        response_dict["errors"]["logo"][0]
        == f'Недопустимый первичный ключ "{str(app_image.id)}" - объект не существует.'
    )


"""
Create widget object when banners and widget apps are unrelated to current partner.
"""


@pytest.mark.skip("blocked by https://jira.7-tech.io/browse/LKX-492")
@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widget_as_partner_owner_with_unrelated_banners(owner_api_client, partner, owner):
    """Test creating widget when banner is unrelated to current partner owner."""

    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create banner that is unrelated to current partner
    banner = BannerFactory.create()

    # Create payload
    data = WidgetDictFactory.build(
        logo=str(app_image.id),
        partner=str(partner.id),
        banners=[str(banner.id)],
        applications=[],
    )

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.post(endpoint, data=data)

    response_dict = response.json()

    # 400 BAS REQUEST is expected
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert (
        response_dict["errors"]["banners"][0]
        == f'Недопустимый первичный ключ "{str(banner.id)}" - объект не существует.'
    )


@pytest.mark.skip("blocked by https://jira.7-tech.io/browse/LKX-492")
@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_put_patch_widget_as_partner_owner_with_unrelated_banners(owner_api_client, owner, partner):
    """Test updating and partially updating widget when banner is unrelated to current partner owner."""

    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create widget
    widget = WidgetFactory.create(
        partner=partner,
        logo=app_image,
        banners=[],
        applications=[],
    )

    # Create banner that is unrelated to current partner
    banner = BannerFactory.create()

    # Create update payload
    data = WidgetDictFactory(
        partner=str(partner.id),
        logo=str(app_image.id),
        banners=[str(banner.id)],
        applications=[],
    )

    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": widget.id})

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_widget = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_widget.delay", mock_send_fcm_to_devices_by_given_widget
    ):

        response = owner_api_client.put(endpoint, data=data)

        response_dict = response.json()

        # 400 BAS REQUEST is expected
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert (
            response_dict["errors"]["banners"][0]
            == f'Недопустимый первичный ключ "{str(banner.id)}" - объект не существует.'
        )

        # Assert that the Celery tasks were called with the expected arguments
        mock_send_fcm_to_devices_by_given_widget.assert_called_once_with(widget.id)


"""
Make requests on widget objects when widget.partner is unrelated to partner owner.
"""


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["get", "put", "patch", "delete"])
def test_make_requests_to_widgets_id_as_partner_owner_without_widget_ownership(owner_api_client, http_method):
    """Test making requests to widgets id when widget is unrelated to partner owner."""

    # When
    widget = WidgetFactory.create()

    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": widget.id})

    http_client_method = getattr(owner_api_client, http_method)

    # Then
    response = http_client_method(endpoint)

    response_dict = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_dict["errors"]["non_field_errors"][0] == "Страница не найдена."


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_by_partner_owner_without_widget_ownership(owner_api_client):
    """Test getting widget when it is unrelated to partner owner."""

    # When
    WidgetFactory.create()

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.get(endpoint)

    response_dict = response.json()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert response_dict["count"] == 0


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_in_csv_by_partner_owner_without_widget_ownership(owner_api_client):
    """Test getting widget in csv format when widget is unrelated to partner owner."""

    # When
    WidgetFactory.create()

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = owner_api_client.get(endpoint)

    # get data from csv
    extracted_data = ReadCSV(response)
    values = extracted_data.values()

    widget_objects_count = Widget.objects.count()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 1

    assert len(values) == 0
