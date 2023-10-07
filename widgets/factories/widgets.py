import uuid

import factory
from factory import DictFactory, Faker, SubFactory
from factory.django import DjangoModelFactory

from apps.widgets.models import Banner, Widget, WidgetApp
from tests.core.factories.images import AppImageObjectFactory, BannerImageObjectFactory
from tests.roles.factories.partners import PartnerFactory


class BannerFactory(DjangoModelFactory):
    name = Faker("name")
    partner = SubFactory(PartnerFactory)
    image = SubFactory(BannerImageObjectFactory)
    link = f"https://{uuid.uuid4()}.com"

    class Meta:
        model = Banner


class BannerDictFactory(DictFactory):
    name = Faker("name")
    partner = SubFactory(PartnerFactory)
    image = SubFactory(BannerImageObjectFactory)
    link = f"https://{uuid.uuid4()}.com"


class WidgetAppFactory(DjangoModelFactory):
    name = Faker("name")
    partner = SubFactory(PartnerFactory)
    image = SubFactory(AppImageObjectFactory)
    link = f"https://{uuid.uuid4()}.com"

    class Meta:
        model = WidgetApp


class WidgetAppDictFactory(DictFactory):
    name = Faker("name")
    partner = SubFactory(PartnerFactory)
    image = SubFactory(AppImageObjectFactory)
    link = f"https://{uuid.uuid4()}.com"


class WidgetFactory(DjangoModelFactory):
    name = Faker("name")
    partner = SubFactory(PartnerFactory)
    logo = SubFactory(AppImageObjectFactory)

    class Meta:
        model = Widget

    @factory.post_generation
    def banners(self, create, extracted):
        if not create:
            return

        if extracted:
            for banner in extracted:
                self.banners.add(banner)

    @factory.post_generation
    def applications(self, create, extracted):
        if not create:
            return

        if extracted:
            for widget_app in extracted:
                self.applications.add(widget_app)


class WidgetDictFactory(DictFactory):
    name = Faker("name")
    partner = SubFactory(PartnerFactory)
    logo = SubFactory(AppImageObjectFactory)
    banners = factory.List([SubFactory(BannerFactory)])
    applications = factory.List([SubFactory(WidgetAppFactory)])
