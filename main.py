from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


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


@app.post("/login")
def login(data: LoginData):
    if data.username == "admin" and data.password == "1234":
        return {"success": True}

    raise HTTPException(
        status_code=401,
        detail="Nieprawidłowy login lub hasło"
    )