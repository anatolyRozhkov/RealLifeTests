from django.urls import reverse

from rest_framework import status

import pytest
from factory import Faker

from apps.widgets.models import Widget
from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory
from tests.utilities.read_csv import ReadCSV
from tests.utilities.time_converter import FilterByDate
from tests.widgets.factories.widgets import BannerFactory, WidgetAppFactory, WidgetFactory

# import dates
dates = FilterByDate()


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
def test_get_widgets_in_csv_as_partner_owner_document_structure(owner_api_client, owner, partner):
    """
    Test downloading widgets in csv format as a partner owner
    and checking document structure.
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
    widget = WidgetFactory.create(partner=partner, banners=[banner], applications=[widget_app], logo=app_image)

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = owner_api_client.get(endpoint)

    # get data from csv
    extracted_data = ReadCSV(response)
    headers = [header.lower() for header in extracted_data.headers()]
    values = extracted_data.values()[0]

    # create response_dict as if the response was in json format
    response_dict = dict(zip(headers, values))

    widget_objects_count = Widget.objects.count()

    # should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 1

    assert len(response_dict) == 6

    assert response_dict["id"] == str(widget.id)
    assert response_dict["название"] == widget.name
    assert response_dict["partner_id"] == str(widget.partner.id)
    assert response_dict["logo_id"] == str(widget.logo.id)
    assert response_dict["частота смены баннеров"] == "0:01:00"
    assert "время создания" in response_dict


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_string, expected_value",
    [
        ("?order_by=created_at", ["month ago", "yesterday", "today"]),
        ("?order_by=name", ["month ago", "today", "yesterday"]),
        ("?ordering=created_at", ["month ago", "yesterday", "today"]),
        ("?ordering=name", ["month ago", "today", "yesterday"]),
    ],
)
def test_get_widgets_in_csv_as_partner_owner_with_order_by(
    owner_api_client, partner, owner, query_string, expected_value
):
    """
    Test downloading widgets filtered order_by, order in csv format as a partner owner.
    """
    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create widget
    WidgetFactory.create(partner=partner, banners=[], applications=[], logo=app_image, name="today")

    # Create widget with created_at=yesterday
    widget_yesterday = WidgetFactory.create(
        partner=partner, name="yesterday", logo=app_image, banners=[], applications=[]
    )
    widget_yesterday.created_at = dates.yesterday
    widget_yesterday.save(update_fields=["created_at"])

    # Create widget with created_at=month ago
    widget_month_ago = WidgetFactory.create(
        partner=partner, name="month ago", logo=app_image, banners=[], applications=[]
    )
    widget_month_ago.created_at = dates.month_ago
    widget_month_ago.save(update_fields=["created_at"])

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    # Get data from csv
    extracted_data = ReadCSV(response)
    values = extracted_data.values()

    widget_objects_count = Widget.objects.count()

    widget_list = [item[2] for item in values]

    # Should return 200 OK
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
def test_get_widgets_in_csv_as_partner_owner_using_name_search_and_search(
    owner_api_client, owner, partner, query_string, expected_value
):
    """
    Test downloading widgets using name__search & search filters in csv format as a partner owner.
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

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    # Get data from csv
    extracted_data = ReadCSV(response)
    headers = [header.lower() for header in extracted_data.headers()]
    values = extracted_data.values()[0]

    # Create response_dict as if the response was in json format
    response_dict = dict(zip(headers, values))

    widget_objects_count = Widget.objects.count()

    # Should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 2

    # Verify that indeed an expected widget was selected
    # Here extracted_data.values() presents a list of lists, where each inner list stores values for single widget
    assert len(extracted_data.values()) == 1
    assert response_dict["название"] == expected_value


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_string, expected_value",
    [
        (f"?created_at__date__gte={dates.today}", 1),
        (f"?created_at__date__lte={dates.yesterday}", 2),
        (f"?created_at__date__gte={dates.month_ago}", 3),
    ],
)
def test_get_widgets_in_csv_as_partner_owner_filtering_by_date(
    owner_api_client, owner, partner, query_string, expected_value
):
    """
    Test downloading widgets filtered by date in csv format as a partner owner.
    """
    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create widget
    WidgetFactory.create(partner=partner, banners=[], applications=[], logo=app_image)

    # Create widget with created_at=yesterday
    widget_yesterday = WidgetFactory.create(partner=partner, logo=app_image, banners=[], applications=[])
    widget_yesterday.created_at = dates.yesterday
    widget_yesterday.save(update_fields=["created_at"])

    # Create widget with created_at=month ago
    widget_month_ago = WidgetFactory.create(partner=partner, logo=app_image, banners=[], applications=[])
    widget_month_ago.created_at = dates.month_ago
    widget_month_ago.save(update_fields=["created_at"])

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    # Get data from csv
    extracted_data = ReadCSV(response)
    values = extracted_data.values()

    widget_objects_count = Widget.objects.count()

    # Should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 3

    assert len(values) == expected_value


@Faker.override_default_locale("ru_RU")
@pytest.mark.django_db
@pytest.mark.parametrize(
    "query_string, expected_value",
    [
        ("?column=created_at&column=partner_id", 2),
        ("?column=name", 1),
    ],
)
def test_get_widgets_in_csv_as_partner_owner_with_column(
    owner_api_client, partner, owner, query_string, expected_value
):
    """
    Test downloading widgets filtered by column in csv format as a partner owner.
    """
    # When
    # Create app image
    app_image = AppImageObjectFactory.create(owner=owner)

    # Create widget
    WidgetFactory.create(partner=partner, banners=[], applications=[], logo=app_image)

    endpoint = reverse("api-root:widgets-export-tabular")

    # Then
    response = owner_api_client.get(endpoint + query_string)

    # Get data from csv
    extracted_data = ReadCSV(response)
    values = extracted_data.values()
    headers = extracted_data.headers()

    widget_objects_count = Widget.objects.count()

    # Should return 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert widget_objects_count == 1

    assert len(values[0]) == expected_value
    assert len(headers) == expected_value
