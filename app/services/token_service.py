import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.schemas.user_schema import UserLogin
from app.services.user_service import get_user_by_username  # Đổi tên cho rõ ràng
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database
# from app.core.config import settings  # Giả sử bạn có file config

# Cấu hình JWT
SECRET_KEY = "cuong_quoc_1401"  # Thay YOUR_SECRET_KEY bằng khóa bí mật của bạn
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

# Cấu hình Passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cấu hình OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db: AsyncIOMotorClient = Depends(get_database), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

async def authenticate_user(db: AsyncIOMotorClient = Depends(get_database), form_data: UserLogin = Depends()):
    user = await get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user