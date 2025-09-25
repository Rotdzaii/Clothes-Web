# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.db import get_db

router = APIRouter()

@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = models.Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        category_id=payload.category_id
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "price": float(p.price), "stock": p.stock,
        "category": p.category.name if p.category else None
    }

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(models.Product).offset(skip).limit(limit).all()
    out = []
    for p in rows:
        out.append({
            "id": p.id, "name": p.name, "description": p.description,
            "price": float(p.price), "stock": p.stock,
            "category": p.category.name if p.category else None
        })
    return out

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.get(models.Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "price": float(p.price), "stock": p.stock,
        "category": p.category.name if p.category else None
    }
