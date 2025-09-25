# insert_users.py
from passlib.context import CryptContext
from app.db import SessionLocal
from app import models

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = [
    ("alice", "alice@example.com", "alice123", "0901234567", "Hà Nội"),
    ("bob", "bob@example.com", "bob123", "0912345678", "TP. HCM"),
    ("charlie", "charlie@example.com", "charlie123", "0923456789", "Đà Nẵng"),
    ("david", "david@example.com", "david123", "0934567890", "Hải Phòng"),
    ("eva", "eva@example.com", "eva123", "0945678901", "Cần Thơ"),
    ("frank", "frank@example.com", "frank123", "0956789012", "Nha Trang"),
    ("grace", "grace@example.com", "grace123", "0967890123", "Huế"),
    ("henry", "henry@example.com", "henry123", "0978901234", "Vũng Tàu"),
    ("ivy", "ivy@example.com", "ivy123", "0989012345", "Quảng Ninh"),
    ("jack", "jack@example.com", "jack123", "0990123456", "Bình Dương"),
]

def main():
    db = SessionLocal()
    try:
        for username, email, plain_pw, phone, address in users:
            # check uniqueness to avoid duplicate key errors
            exists = db.query(models.User).filter(models.User.username == username).first()
            if exists:
                print(f"skip: {username} đã tồn tại (id={exists.id})")
                continue
            hashed = pwd_ctx.hash(plain_pw)
            u = models.User(username=username, email=email, password_hash=hashed, phone=phone, address=address)
            db.add(u)
        db.commit()
        print("Inserted users (where not existed).")
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    main()
