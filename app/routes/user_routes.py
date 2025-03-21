from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserLogin
from app.services.user_service import authenticate_user

router = APIRouter()

@router.post("/login", operation_id="login")
def login(user: UserLogin):
    authenticated_user = authenticate_user(user.username, user.password)
    if authenticated_user:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")