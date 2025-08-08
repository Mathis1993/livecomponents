from django_components import component

from livecomponents import (
    CallContext,
    command,
    InitStateContext,
    LiveComponentsModel,
)
from livecomponents import LiveComponent
from myapp.domain import Item


class InteractivelistState(LiveComponentsModel):
    items: list[Item] = []
    visible_items: list[Item] = []
    no_more_items: bool = False



@component.register("interactivelist")
class InteractivelistComponent(LiveComponent[InteractivelistState]):
    template_name = "interactivelist/interactivelist.html"


    def init_state(self, context: InitStateContext) -> InteractivelistState:
        return InteractivelistState(**context.component_kwargs)

    @command
    def fetch_item(self, call_context: CallContext[InteractivelistState]):
        next_item = call_context.state.items.pop(0) if call_context.state.items else None
        if not next_item :
            call_context.state.no_more_items = True
            return
        call_context.state.visible_items.append(next_item)

    @command
    def remove_item(self, call_context: CallContext[InteractivelistState], item_id: str):
        idx = next((i for i, item in enumerate(call_context.state.visible_items) if item.id == item_id), None)
        if idx is None:
            return
        item = call_context.state.visible_items.pop(idx)
        call_context.state.items.append(item)
        call_context.state.no_more_items = False

