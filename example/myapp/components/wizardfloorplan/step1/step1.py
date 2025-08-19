from django_components import component

from livecomponents import StatelessLiveComponent


@component.register("wizardfloorplan/step1")
class Step1Component(StatelessLiveComponent):
    template_name = "wizardfloorplan/step1/step1.html"
