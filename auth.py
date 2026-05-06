from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException  
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from sqlalchemy.orm import Session
from database import get_db
import models

KEY = os.getenv("KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)  
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": user.id,
            "email": user.email,
            "is_premium": user.is_premium, 
            "name": user.name
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Wrong token")