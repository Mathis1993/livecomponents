from django_components import component

from livecomponents import StatelessLiveComponent


@component.register("wizardfloorplan/step2")
class Step2Component(StatelessLiveComponent):
    template_name = "wizardfloorplan/step2/step2.html"
