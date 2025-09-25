# app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from app import models, schemas
from app.db import get_db

router = APIRouter()

@router.post("/", summary="Create order transactionally")
def create_order(req: schemas.CreateOrderReq, db: Session = Depends(get_db)):
    if not req.items:
        raise HTTPException(status_code=400, detail="No items")

    product_ids = [it.product_id for it in req.items]

    try:
        # Start a DB-level transaction
        with db.begin():
            # Lock selected product rows for update
            products = db.query(models.Product).filter(models.Product.id.in_(product_ids)).with_for_update().all()
            prod_map = {p.id: p for p in products}

            # validate existence & stock
            for it in req.items:
                p = prod_map.get(it.product_id)
                if not p:
                    raise HTTPException(status_code=400, detail=f"Product {it.product_id} not found")
                if p.stock < it.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for product {p.id}")

            order = models.Order(user_id=req.user_id, total_amount=Decimal("0"), status="pending")
            db.add(order)
            db.flush()  # get order.id

            total = Decimal("0")
            for it in req.items:
                p = prod_map[it.product_id]
                p.stock -= it.quantity
                line_total = p.price * it.quantity
                oi = models.OrderItem(order_id=order.id, product_id=p.id,
                                     unit_price=p.price, quantity=it.quantity, line_total=line_total)
                db.add(oi)
                total += line_total

            order.total_amount = total
            # commit happens on exiting with db.begin()
            db.refresh(order)
            # prepare output
            items_out = [{"product_id": oi.product_id, "unit_price": float(oi.unit_price),
                          "quantity": oi.quantity, "line_total": float(oi.line_total)} for oi in order.items]
            return {"order_id": order.id, "total": float(order.total_amount), "items": items_out}
    except HTTPException:
        # re-raise client errors
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
