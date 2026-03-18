from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, get_db
import models
import schemas
import crud

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(data: schemas.RegisterData, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, data.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")

    crud.create_user(db, data.name, data.username, data.password)

    return {"message": "Konto utworzone"}


@app.post("/login")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, data.username)

    if not user or not crud.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane")

    return {"success": True}