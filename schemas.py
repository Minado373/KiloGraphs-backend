from pydantic import BaseModel

class RegisterData(BaseModel):
    name: str
    username: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str