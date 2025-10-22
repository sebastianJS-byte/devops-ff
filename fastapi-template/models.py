from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int