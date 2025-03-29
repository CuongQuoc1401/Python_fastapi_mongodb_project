# app/services/user_service.py
from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database
from app.utils.security import verify_password, hash_password
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse  # Import schemas

async def get_user_by_username(db: AsyncIOMotorClient, username: str):
    return await db["users"].find_one({"username": username})

async def create_user(db: AsyncIOMotorClient, user: UserCreate):
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = hash_password(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    user_dict.pop("confirm_password", None)  # Remove confirm_password field
    result = await db["users"].insert_one(user_dict)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    return UserResponse(**created_user)

async def authenticate_user(db: AsyncIOMotorClient = Depends(get_database), form_data: UserLogin = Depends()):
    user = await get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user

async def authenticate_username(db: AsyncIOMotorClient = Depends(get_database), username: str = Depends()):
    return await get_user_by_username(db, username)