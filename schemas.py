from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterData(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str