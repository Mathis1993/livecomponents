from typing import Any
from django_components import component
from livecomponents import StatelessLiveComponent


@component.register("wizardfloorplan/price")
class PriceComponent(StatelessLiveComponent):
    template_name = "wizardfloorplan/price/price.html"
