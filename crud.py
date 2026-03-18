from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, name: str, username: str, password: str):
    hashed_password = hash_password(password)

    user = User(
        name=name,
        username=username,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user