from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user_schema import UserLogin
from app.services.user_service import authenticate_user
from app.services.token_service import create_access_token
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database

router = APIRouter()
# router = APIRouter(prefix="/api") # Định nghĩa prefix cho router

@router.post("/login", operation_id="login")
async def login_for_access_token(db: AsyncIOMotorClient = Depends(get_database), user: UserLogin = Depends()):
    authenticated_user = await authenticate_user(db, user.username, user.password)
    if authenticated_user:
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")