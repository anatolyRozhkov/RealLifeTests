from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Widget
from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory
from tests.widgets.factories.widgets import BannerFactory, WidgetAppFactory, WidgetDictFactory


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_post_widgets_as_partner_owner(owner_api_client, partner, owner):
    """Test creating widgets as partner owner."""

    # When
    # Create images
    banner_image = BannerImageObjectFactory.create(owner=owner)
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create banner
    banner = BannerFactory.create(partner=partner, image=banner_image)

    # Create widget app
    widget_app = WidgetAppFactory.create(partner=partner, image=app_image)

    # Populate payload
    data = WidgetDictFactory.build(
        partner=str(partner.id), banners=[str(banner.id)], applications=[str(widget_app.id)], logo=str(app_image.id)
    )

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.post(endpoint, data=data)

    response_dict = response.json()

    list_of_widgets = [widget for widget in Widget.objects.all()]

    # expected output 201_CREATED
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response_dict) == 8
    assert len(list_of_widgets) == 1
    first_widget = list_of_widgets[0]

    assert response_dict["id"] == str(first_widget.id)
    assert response_dict["partner"] == data["partner"]
    assert response_dict["name"] == data["name"]
    assert response_dict["change_frequency"] == "00:01:00"
    assert response_dict["logo"] == data["logo"]

    assert len(response_dict["banners"]) == 1
    assert response_dict["banners"][0] == data["banners"][0]

    assert len(response_dict["applications"]) == 1
    assert response_dict["applications"][0] == data["applications"][0]

    assert "created_at" in response_dict
