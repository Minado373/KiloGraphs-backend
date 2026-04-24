from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, name: str, email: str, password: str):
    hashed_password = hash_password(password)

    user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def set_user_premium(db: Session, user_id: int, stripe_cust_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_premium = True
        user.stripe_customer_id = stripe_cust_id
        db.commit()
    return user