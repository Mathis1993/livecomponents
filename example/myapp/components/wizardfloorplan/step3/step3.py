from django_components import component

from livecomponents import StatelessLiveComponent


@component.register("wizardfloorplan/step3")
class Step3Component(StatelessLiveComponent):
    template_name = "wizardfloorplan/step3/step3.html"
