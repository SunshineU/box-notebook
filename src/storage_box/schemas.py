from pydantic import BaseModel
from datetime import datetime


# ============== 用户相关 ==============
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ============== 物品相关 ==============
class Item(BaseModel):
    id: int | None = None
    user_id: int
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
