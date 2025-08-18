from django_components import component

from livecomponents import StatelessLiveComponent


@component.register("wizardfloorplan/navigation")
class NavigationComponent(StatelessLiveComponent):
    template_name = "wizardfloorplan/navigation/navigation.html"
