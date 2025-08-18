from typing import Any, Optional, Union
from django import forms
from django_components import component

from livecomponents import (
    CallContext,
    command,
    ExtraContextRequest,
    InitStateContext,
    LiveComponentsModel,
)

from livecomponents import LiveComponent
from myapp.models import FloorPlanOrder


class QuantityForm(forms.ModelForm):
    class Meta:
        model = FloorPlanOrder
        fields = ["quantity"]

    quantity = forms.IntegerField(min_value=1)


class ResolutionForm(forms.ModelForm):
    class Meta:
        model = FloorPlanOrder
        fields = ["resolution"]

    resolution = forms.ChoiceField(
        choices=FloorPlanOrder.Resolution.choices,
        required=True,
        widget=forms.Select,
        label="Resolution",
    )


class Step2Form2D(forms.ModelForm):
    class Meta:
        model = FloorPlanOrder
        fields = ["show_furniture"]

    show_furniture = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"role": "switch"}),
    )


class Step2Form3D(forms.ModelForm):
    class Meta:
        model = FloorPlanOrder
        fields = ["furniture_style", "show_measurements"]

    furniture_style = forms.ChoiceField(
        choices=FloorPlanOrder.FurnitureStyle.choices,
        required=True,
        widget=forms.Select,
    )
    show_measurements = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"role": "switch"}),
    )


class Step3Form(forms.ModelForm):
    class Meta:
        model = FloorPlanOrder
        fields = ["customer_first_name", "customer_last_name", "street", "postcode", "city", "country"]
        labels = {
            "customer_first_name": "First Name",
            "customer_last_name": "Last Name",
        }

    country = forms.ChoiceField(
        choices=FloorPlanOrder.Country.choices,
        required=True,
        widget=forms.Select,
    )

    def clean_postcode(self):
        postcode = self.cleaned_data.get("postcode", "")
        if not postcode.isdigit() or len(postcode) != 5:
            raise forms.ValidationError("Postcode must be a 5-digit number.")
        return postcode


class RootState(LiveComponentsModel):
    step: int = 1
    highest_step_visited: int = 1
    finished: bool = False
    floor_plan_order: FloorPlanOrder
    quantity_form: QuantityForm | None = None
    resolution_form: ResolutionForm | None = None
    step2_form_class: type[Union[Step2Form2D, Step2Form3D]] | None = None
    step2_form: Union[Step2Form2D, Step2Form3D] | None = None
    step3_form: Step3Form | None = None

    def init_quantity_form(self):
        self.quantity_form = QuantityForm(instance=self.floor_plan_order)

    def init_resolution_form(self):
        if self.floor_plan_order.dimension == FloorPlanOrder.Dimension.THREE_DIMENSIONAL:
            self.resolution_form = None
        else:
            self.resolution_form = ResolutionForm(instance=self.floor_plan_order)

    def init_step2_form(self):
        if self.floor_plan_order.dimension == FloorPlanOrder.Dimension.TWO_DIMENSIONAL:
            self.init_resolution_form()
            self.step2_form_class = Step2Form2D
            self.step2_form = Step2Form2D(instance=self.floor_plan_order)
        elif self.floor_plan_order.dimension == FloorPlanOrder.Dimension.THREE_DIMENSIONAL:
            self.step2_form_class = Step2Form3D
            self.step2_form = Step2Form3D(instance=self.floor_plan_order)

    def init_step3_form(self):
        self.step3_form = Step3Form(instance=self.floor_plan_order)


@component.register("wizardfloorplan/root")
class RootComponent(LiveComponent[RootState]):
    template_name = "wizardfloorplan/root/root.html"

    def get_extra_context_data(
            self, extra_context_request: ExtraContextRequest[RootState]
    ) -> dict[str, Any]:
        return {
            "steps": ["Step 1", "Step 2", "Step 3"],
            "dimension_2D": FloorPlanOrder.Dimension.TWO_DIMENSIONAL,
            "dimension_3D": FloorPlanOrder.Dimension.THREE_DIMENSIONAL,
            "price_2D": FloorPlanOrder.PRICE_2D,
            "price_3D": FloorPlanOrder.PRICE_3D,
        }

    def init_state(self, context: InitStateContext) -> RootState:
        context.component_kwargs.setdefault(
            "floor_plan_order",
            FloorPlanOrder(
                dimension=FloorPlanOrder.Dimension.TWO_DIMENSIONAL,
                show_furniture=False,
                resolution=FloorPlanOrder.Resolution.HD,
                furniture_style=FloorPlanOrder.FurnitureStyle.ARCHAIC,
                show_measurements=False,
                quantity=1,
            ),
        )
        return RootState(**context.component_kwargs)

    @command
    def finish_step1(self, call_context: CallContext[RootState], dimension: str):
        state = call_context.state
        state.floor_plan_order.dimension = dimension
        state.init_quantity_form()
        state.init_resolution_form()
        state.init_step2_form()
        state.step = 2
        state.highest_step_visited = max(state.highest_step_visited, 2)

    @command
    def finish_step2(self, call_context: CallContext[RootState], **kwargs):
        state = call_context.state
        state.step2_form = state.step2_form_class(instance=state.floor_plan_order, data=kwargs)
        if state.step2_form.is_valid():
            state.floor_plan_order = state.step2_form.save(commit=False)
            state.init_step3_form()
            state.step = 3
            state.highest_step_visited = 3

    @command
    def finish_step3(self, call_context: CallContext[RootState], **kwargs):
        state = call_context.state
        state.step3_form = Step3Form(instance=state.floor_plan_order, data=kwargs)
        if state.step3_form.is_valid():
            state.floor_plan_order = state.step3_form.save(commit=False)
            state.finished = True
            state.floor_plan_order.save()

    @command
    def set_step(self, call_context: CallContext[RootState], step: int):
        state = call_context.state
        if step < 1 or step > 3:
            raise ValueError("Step must be between 1 and 3.")
        if step == 2:
            state.init_resolution_form()
        state.step = step

    @command
    def update_price(self, call_context: CallContext[RootState], **kwargs):
        state = call_context.state
        if "quantity" in kwargs:
            state.quantity_form = QuantityForm(instance=state.floor_plan_order, data=kwargs)
            if state.quantity_form.is_valid():
                state.floor_plan_order.quantity = state.quantity_form.cleaned_data["quantity"]
        if "dimension" in kwargs:
            state.floor_plan_order.dimension = kwargs["dimension"]
        if "resolution" in kwargs:
            state.floor_plan_order.resolution = kwargs["resolution"]