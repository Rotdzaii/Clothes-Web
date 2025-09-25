# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models, schemas
from app.db import get_db

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # simple uniqueness checks
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="username exists")
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="email exists")

    hashed = pwd_ctx.hash(payload.password)
    u = models.User(username=payload.username, email=payload.email, password_hash=hashed)
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"id": u.id, "username": u.username, "email": u.email}
