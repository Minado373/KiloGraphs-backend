from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False) 

    profile = relationship("Profile", back_populates="user", uselist=False)
    diet_plans = relationship("DietPlan", back_populates="user")
    training_plans = relationship("TrainingPlan", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gender = Column(String)
    age = Column(Integer)
    weight = Column(Float)   
    height = Column(Float)   
    goal = Column(String)
    activity_level = Column(String)
    additional_info = Column(Text)
    calories = Column(Float) 

    user = relationship("User", back_populates="profile")


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    date = Column(DateTime, server_default=func.now())
    target_calories = Column(Integer)
    target_water_ml = Column(Integer)
    meals_data = Column(Text)  

    user = relationship("User", back_populates="diet_plans")


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    generated_at = Column(DateTime, server_default=func.now())
    days_data = Column(Text) 

    user = relationship("User", back_populates="training_plans")