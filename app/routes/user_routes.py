from fastapi import APIRouter, HTTPException, Depends, Body
from app.schemas.user_schema import UserLogin, UserCreate, UserResponse
from app.services.user_service import authenticate_user, create_user, get_user_by_username
from app.services.token_service import create_access_token
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database
from typing import Optional

router = APIRouter()
# router = APIRouter(prefix="/api") # Định nghĩa prefix cho router

@router.post("/register", response_model=UserResponse, operation_id="register")
async def register_user(user: UserCreate = Body(..., description="Thông tin người dùng để đăng ký"), db: AsyncIOMotorClient = Depends(get_database)):
    """
    Đăng ký một người dùng mới.
    """
    return await create_user(db, user)

@router.post("/login", operation_id="login")
async def login_for_access_token(
    db: AsyncIOMotorClient = Depends(get_database),
    user: UserLogin = Body(..., description="Thông tin đăng nhập người dùng")
):
    """
    Đăng nhập người dùng và trả về access token.
    """
    authenticated_user = await authenticate_user(db, user)
    if authenticated_user:
        access_token = create_access_token(data={"sub": authenticated_user['username']})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không hợp lệ")

@router.get("/users/{username}", response_model=Optional[UserResponse], operation_id="get_user")
async def get_user(username: str, db: AsyncIOMotorClient = Depends(get_database)):
    """
    Lấy thông tin người dùng dựa trên username.
    """
    user = await get_user_by_username(db, username)
    if user:
        return UserResponse(**user)
    raise HTTPException(status_code=404, detail=f"Không tìm thấy người dùng với username: {username}")

# Bạn có thể thêm các route khác liên quan đến người dùng ở đây, ví dụ:
# - Cập nhật thông tin người dùng (PUT /users)
# - Xóa người dùng (DELETE /users/{username})
# - Lấy danh sách người dùng (GET /users) - cần cân nhắc về bảo mật