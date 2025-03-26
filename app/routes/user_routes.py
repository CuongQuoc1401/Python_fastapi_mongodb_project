from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserLogin
from app.services.user_service import authenticate_user
from app.services.token_service import create_access_token

router = APIRouter()
# router = APIRouter(prefix="/api") # Định nghĩa prefix cho router

@router.post("/login", operation_id="login")
async def login_for_access_token(user: UserLogin):
    authenticated_user = authenticate_user(user.username, user.password)
    if authenticated_user:
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
