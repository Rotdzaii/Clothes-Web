# app/models.py (merge rồi)
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from .db import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(12,2), nullable=False)
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", lazy="joined")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # store bcrypt hash
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Numeric(12,2), default=0)
    status = Column(String(30), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", lazy="joined")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    unit_price = Column(Numeric(12,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Numeric(12,2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    order = relationship("Order", back_populates="items")
    product = relationship("Product", lazy="joined")
