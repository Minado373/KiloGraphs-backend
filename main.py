from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, get_db
import models
import schemas
import crud
from auth import create_access_token, get_current_user
from dotenv import load_dotenv
import os

from ai_service import generate_plan
from utils import calculate_calories, build_prompt

Base.metadata.create_all(bind=engine)

load_dotenv()
stripe_api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL")

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
    
    return {"message": "Account created", "user_id": user.id}

@app.post("/login")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)

    if not user or not crud.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "is_premium": user.is_premium
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


@app.post("/create-checkout-session")
def create_checkout(user=Depends(get_current_user)):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1TOxgJ8MhBMmVHwX1GEvVJkM', 
                'quantity': 1,
            }],
            mode='subscription', # Tryb subskrypcji
            success_url=f"${FRONTEND_URL}/success",
            cancel_url=f"${FRONTEND_URL}/cancel",
            client_reference_id=str(user["user_id"]),
            customer_email=user["email"]
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook Error: {str(e)}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        stripe_cust_id = session.get('customer')

        if user_id:
            crud.set_user_premium(db, user_id=int(user_id), stripe_cust_id=stripe_cust_id)
            print(f"Baza Neon zaktualizowana dla użytkownika {user_id}")

    return {"status": "success"}

@app.post("/generate-plan", response_model=schemas.FullPlanResponse)
def generate_plan_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = user["user_id"]
    
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    current_calories = calculate_calories(profile)

    seven_days_ago = datetime.now() - timedelta(days=7)


    existing_diet = db.query(models.DietPlan).filter(
        models.DietPlan.user_id == user_id,
        models.DietPlan.date >= seven_days_ago
    ).order_by(models.DietPlan.id.desc()).first()

    existing_training = db.query(models.TrainingPlan).filter(
        models.TrainingPlan.user_id == user_id,
        models.TrainingPlan.generated_at >= seven_days_ago
    ).order_by(models.TrainingPlan.id.desc()).first()

    if existing_diet and existing_training:
        if existing_diet.target_calories == current_calories:
            return {
                "diet": existing_diet.meals_data,
                "training": existing_training.days_data
            }
    
    prompt = build_prompt(profile, current_calories)
    diet, training = generate_plan(prompt)

    new_diet = models.DietPlan(
        user_id=user_id,
        target_calories=current_calories,
        meals_data=diet,
        date=datetime.now()
    )
    db.add(new_diet)

    new_training = models.TrainingPlan(
        user_id=user_id,
        days_data=training,
        generated_at=datetime.now()
    )
    db.add(new_training)

    db.commit()

    return {
        "diet": diet,
        "training": training
    }

@app.get("/my-plan/{user_id}")
def get_my_plan(
    user_id: int, 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    diet = db.query(models.DietPlan).filter(models.DietPlan.user_id == user_id).order_by(models.DietPlan.id.desc()).first()
    training = db.query(models.TrainingPlan).filter(models.TrainingPlan.user_id == user_id).order_by(models.TrainingPlan.id.desc()).first()

    return {
        "diet": diet.meals_data if diet else None,
        "training": training.days_data if training else None
    }
