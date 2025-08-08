from pydantic import BaseModel


class Item(BaseModel):
    id: str
    text: str