from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from .db import get_db, engine

app = FastAPI(title="Shop Demo - DB Check")

@app.get("/")
def root():
    return {"ok": True, "message": "Dzô"}

@app.get("/dbcheck")
def db_check():
    # quick raw check using engine
    try:
        with engine.connect() as conn:
            r = conn.execute(text("SELECT 1")).scalar()
            return {"db_ok": True, "result": int(r)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
