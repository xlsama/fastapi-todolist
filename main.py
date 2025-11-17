from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class FruitName(str, Enum):
    apple = "apple"
    banana = "banana"
    orange = "orange"


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.get("/fruits/{fruit_name}")
async def get_fruit(fruit_name: FruitName):
    if fruit_name is FruitName.apple:
        return {"fruit_name": fruit_name, "message": "Apple is good for your health"}

    if fruit_name is FruitName.banana:
        return {"fruit_name": fruit_name, "message": "Banana is good for your health"}

    return {"fruit_name": fruit_name, "message": "Orange is good for your health"}
