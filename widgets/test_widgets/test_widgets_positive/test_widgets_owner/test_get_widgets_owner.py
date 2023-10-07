from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Widget
from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory
from tests.utilities.time_converter import FilterByDate
from tests.widgets.factories.widgets import BannerFactory, WidgetAppFactory, WidgetFactory

# import dates
dates = FilterByDate()


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_string, expected_value",
    [
        ("?limit=2", 2),
        (f"?created_at__date__gte={dates.today}", 1),
        (f"?created_at__date__lte={dates.yesterday}", 2),
        (f"?created_at__date__gte={dates.month_ago}", 3),
        ("?offset=1", 2),
    ],
)
def test_get_widgets_as_partner_owner_filtering_by_date_limit_offset(
    owner_api_client, partner, query_string, expected_value
):
    """
    Test listing widgets as partner owner filtering by limit, date, offset.
    """
    # When
    # Create first widget
    WidgetFactory.create(partner=partner)

    # Create second widget (created_at=yesterday)
    widget_yesterday = WidgetFactory.create(partner=partner)
    widget_yesterday.created_at = dates.yesterday
    widget_yesterday.save(update_fields=["created_at"])

    # Create third widget (created_at=month ago)
    widget_month_ago = WidgetFactory.create(partner=partner)
    widget_month_ago.created_at = dates.month_ago
    widget_month_ago.save(update_fields=["created_at"])

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    response_dict = response.json()
    widget_objects_count = Widget.objects.count()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 3

    assert len(response_dict["results"]) == expected_value


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_string, expected_value",
    [
        ("?order_by=created_at", ["month ago", "yesterday", "today"]),
        ("?order_by=name", ["month ago", "today", "yesterday"]),
    ],
)
def test_get_widgets_as_partner_owner_with_order_by(owner_api_client, partner, query_string, expected_value):
    """
    Test listing widgets as partner owner ordering by name, created_at.
    """
    # When
    # Create first widget
    WidgetFactory.create(partner=partner, name="today")

    # Create second widget (created_at=yesterday)
    widget_yesterday = WidgetFactory.create(partner=partner, name="yesterday")
    widget_yesterday.created_at = dates.yesterday
    widget_yesterday.save(update_fields=["created_at"])

    # Create third widget (created_at=month ago)
    widget_month_ago = WidgetFactory.create(partner=partner, name="month ago")
    widget_month_ago.created_at = dates.month_ago
    widget_month_ago.save(update_fields=["created_at"])

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    response_dict = response.json()
    widget_objects_count = Widget.objects.count()

    widget_list = [widget["name"] for widget in response_dict["results"]]

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 3

    assert widget_list == expected_value


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_string, expected_value",
    [
        ("?name__search=today", "today"),
        ("?name__search=month ago", "month ago"),
        ("?search=month ago", "month ago"),
    ],
)
def test_get_widgets_as_partner_owner_using_name_search_and_search(
    owner_api_client, owner, partner, query_string, expected_value
):
    """
    Test listing widgets using name__search & search filters as a partner owner.
    """
    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create widget
    WidgetFactory.create(partner=partner, banners=[], applications=[], logo=app_image, name="today")

    # Create widget with created_at=month ago
    widget_month_ago = WidgetFactory.create(
        partner=partner, logo=app_image, banners=[], applications=[], name="month ago"
    )
    widget_month_ago.created_at = dates.month_ago
    widget_month_ago.save(update_fields=["created_at"])

    endpoint = reverse("api-root:widgets-list")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    response_dict = response.json()

    widget_objects_count = Widget.objects.count()

    # Should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 2

    # Verify that indeed an expected widget was selected
    assert len(response_dict["results"]) == 1
    retrieved_widget = response_dict["results"][0]

    assert retrieved_widget["name"] == expected_value


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widget_by_id_as_partner_owner(owner_api_client, owner, partner):
    """Test retrieving a widget by partner owner."""

    # When
    # Create images
    banner_image = BannerImageObjectFactory.create(owner=owner)
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create banner
    banner = BannerFactory.create(partner=partner, image=banner_image)

    # Create widget app
    widget_app = WidgetAppFactory.create(partner=partner, image=app_image)

    # Create widget
    widget = WidgetFactory.create(partner=partner, banners=[banner], applications=[widget_app], logo=app_image)

    endpoint = reverse("api-root:widgets-detail", kwargs={"pk": widget.id})

    # Then
    response = owner_api_client.get(endpoint)

    response_dict = response.json()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert len(response_dict) == 8

    assert response_dict["id"] == str(widget.id)
    assert response_dict["partner"] == str(widget.partner.id)
    assert response_dict["name"] == widget.name
    assert response_dict["change_frequency"] == "00:01:00"

    assert len(response_dict["banners"]) == 1
    first_banner = response_dict["banners"][0]

    assert first_banner["id"] == str(banner.id)
    assert first_banner["partner"] == str(banner.partner.id)
    assert first_banner["name"] == banner.name
    assert first_banner["link"] == banner.link
    assert "created_at" in first_banner

    assert len(first_banner["image"]) == 6
    first_banner_image = first_banner["image"]

    assert first_banner_image["id"] == str(banner.image.id)
    assert first_banner_image["owner"] == str(banner.image.owner.id)
    assert first_banner_image["name"] == banner.image.name
    assert "image" in first_banner_image
    assert "file_size" in first_banner_image
    assert "created_at" in first_banner_image

    assert len(response_dict["applications"]) == 1
    first_widget_app = response_dict["applications"][0]

    assert first_widget_app["id"] == str(widget_app.id)
    assert first_widget_app["partner"] == str(widget_app.partner.id)
    assert first_widget_app["name"] == widget_app.name
    assert first_widget_app["link"] == widget_app.link
    assert "created_at" in first_widget_app

    assert len(first_widget_app["image"]) == 6
    first_widget_app_image = first_widget_app["image"]

    assert first_widget_app_image["id"] == str(widget_app.image.id)
    assert first_widget_app_image["owner"] == str(widget_app.image.owner.id)
    assert first_widget_app_image["name"] == widget_app.image.name
    assert "image" in first_widget_app_image
    assert "file_size" in first_widget_app_image
    assert "created_at" in first_widget_app_image

    assert len(response_dict["logo"]) == 6
    logo = response_dict["logo"]

    assert logo["id"] == str(widget.logo.id)
    assert logo["owner"] == str(widget.logo.owner.id)
    assert logo["name"] == widget.logo.name
    assert "image" in logo
    assert "file_size" in logo
    assert "created_at" in logo

    assert "created_at" in response_dict
