from pydantic import BaseModel
from datetime import datetime


class Item(BaseModel):
    id: int | None = None
    name: str
    category: str
    location: str
    quantity: int = 1
    notes: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class ItemCreate(BaseModel):
    name: str
    category: str
    location: str
    quantity: int = 1
    notes: str = ""


class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    location: str | None = None
    quantity: int | None = None
    notes: str | None = None
