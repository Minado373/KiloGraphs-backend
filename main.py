from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, get_db
import models
import schemas
import crud
from auth import create_access_token, get_current_user


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
    print("REGISTER DATA:", data)
    existing_user = crud.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = crud.create_user(db, data.name, data.email, data.password)
    # Zmieniono: "Konto utworzone" -> "Account created"
    return {"message": "Account created", "user_id": user.id}

@app.post("/login")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)

    if not user or not crud.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name
    }

@app.post("/profile")
def save_profile(
    data: schemas.ProfileCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)  
):
    user_id = user["user_id"] 

    user_obj = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    
    if not profile:
        profile = models.Profile(user_id=user_id)
        db.add(profile)

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
def get_profile(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile