# app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category_id: Optional[int] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str] = None

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}

class CartItem(BaseModel):
    product_id: int
    quantity: int

class CreateOrderReq(BaseModel):
    user_id: int
    items: List[CartItem]

class OrderItemOut(BaseModel):
    product_id: int
    unit_price: float
    quantity: int
    line_total: float

class OrderOut(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    items: List[OrderItemOut]

    model_config = {"from_attributes": True}
