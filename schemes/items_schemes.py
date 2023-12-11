from pydantic import BaseModel

class BaseItem(BaseModel):
    name: str
    quantity: int

    class Config():
        orm_mode=True

class Item(BaseItem):
    id: int

    class Config():
        orm_mode=True

class ItemInput(BaseItem):
    pass

