import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.schemas.user_schema import UserLogin
from app.services.user_service import authenticate_user, authenticate_username

# Cấu hình JWT
SECRET_KEY = "cuong_quoc_1401"  # Thay YOUR_SECRET_KEY bằng khóa bí mật của bạn
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Cấu hình Passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cấu hình OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta is None:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    # user = authenticate_user(username, "")  # Thay "" bằng mật khẩu (nếu cần)
    user = authenticate_username(username)  # Thay "" bằng mật khẩu (nếu cần)
    if user is None:
        raise credentials_exception
    return user