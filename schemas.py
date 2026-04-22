from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterData(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class CaloriesCreate(BaseModel):
    user_id: int
    calories: float

class ProfileCreate(BaseModel):
    user_id: int
    gender: Optional[str] = "Male"
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: Optional[str] = "Weight Loss"
    activity_level: Optional[str] = "0"
    additional_info: Optional[str] = None
    calories: Optional[float] = None

    class Config:
        from_attributes = True

class FullPlanResponse(BaseModel):
    diet: str
    training: str
