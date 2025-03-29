from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database
from app.utils.security import verify_password

async def authenticate_user(username: str, password: str, db: AsyncIOMotorClient = Depends(get_database)):
    print(f"Authenticating user: {username}")
    user = await db["users"].find_one({"username": username})
    print(f"User found: {user}")
    if user and verify_password(user["password"], password):
        print("Authentication successful")
        return user
    print("Authentication failed")
    return None

async def authenticate_username(username: str, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db["users"].find_one({"username": username})
    if user:
        return user
    return None