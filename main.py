from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, get_db
import models
import schemas
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KiloGraphs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(data: schemas.RegisterData, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")
    user = crud.create_user(db, data.name, data.email, data.password)
    return {"message": "Konto utworzone", "user_id": user.id}

@app.post("/login")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user or not crud.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane")
    return {"success": True, "user_id": user.id, "name": user.name}

@app.post("/profile")
def save_profile(data: schemas.ProfileCreate, db: Session = Depends(get_db)):
    # Sprawdzenie czy użytkownik istnieje
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Szukanie profilu - jeśli nie ma, stwórz nowy
    profile = db.query(models.Profile).filter(models.Profile.user_id == data.user_id).first()
    
    if not profile:
        profile = models.Profile(user_id=data.user_id)
        db.add(profile)

    # Aktualizacja danych
    profile.gender = data.gender
    profile.age = data.age
    profile.weight = data.weight
    profile.height = data.height
    profile.goal = data.goal
    profile.activity_level = data.activity_level
    profile.additional_info = data.additional_info
    profile.calories = data.calories

    db.commit()
    db.refresh(profile)
    return {"message": "Profile saved", "profile_id": profile.id}

@app.get("/profile/{user_id}", response_model=schemas.ProfileCreate)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile