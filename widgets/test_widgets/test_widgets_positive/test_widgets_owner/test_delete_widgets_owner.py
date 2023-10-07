from unittest.mock import Mock, patch

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Widget
from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory
from tests.widgets.factories.widgets import BannerFactory, WidgetAppFactory, WidgetFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_delete_widget_as_partner_owner(owner_api_client, partner):
    """Test destroying widget as partner owner."""

    # When
    # Create widget
    widget = WidgetFactory.create(partner=partner)

    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": widget.id})

    # Then
    response = owner_api_client.delete(endpoint)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Widget.objects.filter(id=widget.id).exists()


"""
Test remove_banners
"""


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_delete_widget_banner_as_partner_owner(owner_api_client, owner, partner):
    """Test deleting banner from a widget object as partner owner."""

    # When
    # Create banner image
    banner_image = BannerImageObjectFactory.create(owner=owner)

    # Create banner
    banner = BannerFactory.create(partner=partner, image=banner_image)

    # Create widget
    widget = WidgetFactory.create(partner=partner, banners=[banner])

    endpoint = reverse("api-root:widgets-remove-banners", kwargs={"pk": widget.id})

    # Get banner associated with this widget before deleting it
    widget_with_prefetched_banners = Widget.objects.prefetch_related("banners").get(id=widget.id)
    num_of_banners_before = widget_with_prefetched_banners.banners.count()

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_widget = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_widget.delay", mock_send_fcm_to_devices_by_given_widget
    ):

        response = owner_api_client.delete(endpoint + f"?ids={banner.id}")

        # Get banners associated with this widget
        updated_widget_with_prefetched_banners = Widget.objects.prefetch_related("banners").get(id=widget.id)
        num_of_banners_after = updated_widget_with_prefetched_banners.banners.count()

        # should return 200 OK
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert num_of_banners_before == 1
        assert num_of_banners_after == 0

        # Assert that the Celery tasks were called with the expected arguments
        mock_send_fcm_to_devices_by_given_widget.assert_called_once_with(widget.id)


"""
Test remove_widget_apps
"""


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_delete_widget_widget_app_as_partner_owner(owner_api_client, owner, partner):
    """Test deleting widget apps from a widget object as partner owner."""

    # When
    # Create widget image
    widget_image = AppImageObjectFactory.create(owner=owner)

    # Create widget app
    widget_app = WidgetAppFactory.create(partner=partner, image=widget_image)

    # Create widget
    widget = WidgetFactory.create(partner=partner, applications=[widget_app])

    endpoint = reverse("api-root:widgets-remove-widget-apps", kwargs={"pk": widget.id})

    # Get widget app associated with this widget before deleting it
    widget_with_prefetched_widget_apps = Widget.objects.prefetch_related("applications").get(id=widget.id)
    num_of_widget_apps_before = widget_with_prefetched_widget_apps.applications.count()

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_widget = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_widget.delay", mock_send_fcm_to_devices_by_given_widget
    ):

        response = owner_api_client.delete(endpoint + f"?ids={widget_app.id}")

        # Get widget apps associated with this widget
        updated_widget_with_prefetched_widget_apps = Widget.objects.prefetch_related("applications").get(id=widget.id)
        num_of_widget_apps_after = updated_widget_with_prefetched_widget_apps.banners.count()

        # should return 200 OK
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert num_of_widget_apps_before == 1
        assert num_of_widget_apps_after == 0

        # Assert that the Celery tasks were called with the expected arguments
        mock_send_fcm_to_devices_by_given_widget.assert_called_once_with(widget.id)
