import uuid
from unittest.mock import Mock, patch

from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory
from tests.roles.factories.partners import PartnerFactory
from tests.widgets.factories.widgets import BannerFactory, WidgetAppFactory, WidgetDictFactory, WidgetFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize("http_method", ["put", "patch"])
def test_put_patch_widgets_as_partner_owner(http_method, owner_api_client, owner, partner):
    """Test updating and partially updating widgets as partner owner.

    According to WidgetUpdateSerializer
    new widget_apps can be added to applications
    new banners can be added to banners
    name, link, and logo attributes can be replaced.
    """

    # When
    # Create images
    banner_image = BannerImageObjectFactory.create(owner=owner)
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create banner
    banner = BannerFactory.create(partner=partner, image=banner_image)

    # Create widget app
    widget_app = WidgetAppFactory.create(partner=partner, image=app_image)

    # Create widget
    widget = WidgetFactory.create(partner=partner, applications=[widget_app], banners=[banner], logo=app_image)

    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": widget.id})

    # Create new objects to update widget with
    new_banner = BannerFactory.create(partner=partner, image=banner_image)
    new_widget_app = WidgetAppFactory.create(partner=partner, image=app_image)
    new_logo = AppImageObjectFactory.create(owner=owner)
    new_partner = PartnerFactory.create()

    # Create payload
    data = WidgetDictFactory.build(
        # This should be updated
        logo=str(new_logo.id),
        name=Faker("name"),
        link=f"https://{uuid.uuid4()}.com",
        # New values will be added to applications and banners
        applications=[str(new_widget_app.id)],
        banners=[str(new_banner.id)],
        # This should not be updated
        partner=str(new_partner.id),
        change_frequency="00:02:00",
    )

    http_client_method = getattr(owner_api_client, http_method)

    # Create Mock objects for the Celery tasks
    mock_send_fcm_to_devices_by_given_widget = Mock()

    # Then

    # Patch the Celery tasks with the Mock objects
    with patch(
        "apps.devices.tasks.send_fcm_to_devices_by_given_widget.delay", mock_send_fcm_to_devices_by_given_widget
    ):

        response = http_client_method(endpoint, data=data)

        response_dict = response.json()

        # should return 200 OK
        assert response.status_code == status.HTTP_200_OK
        assert len(response_dict) == 8
        assert "created_at" in response_dict

        # protected fields
        assert response_dict["id"] == str(widget.id)
        assert response_dict["partner"] == str(partner.id)
        assert response_dict["change_frequency"] == "00:01:00"

        # updated fields
        assert response_dict["name"] == data["name"]
        assert response_dict["logo"] == data["logo"]

        assert len(response_dict["banners"]) == 2
        first_banner = response_dict["banners"][1]
        second_banner = response_dict["banners"][0]

        assert first_banner == str(banner.id)
        assert second_banner == str(new_banner.id)

        assert len(response_dict["applications"]) == 2
        first_widget_app = response_dict["applications"][1]
        second_widget_app = response_dict["applications"][0]

        assert first_widget_app == str(widget_app.id)
        assert second_widget_app == str(new_widget_app.id)

        # Assert that the Celery tasks were called with the expected arguments
        mock_send_fcm_to_devices_by_given_widget.assert_called_once_with(widget.id)
