from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
import bcrypt
import hashlib
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.waitstaff import Waitstaff
from app.core.database import get_db

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Sử dụng phương pháp xác thực đơn giản với MD5 thay vì bcrypt
    cho mục đích kiểm thử
    """
    try:
        # Sử dụng MD5 để kiểm tra mật khẩu
        md5_hash = hashlib.md5(plain_password.encode()).hexdigest()
        result = md5_hash == hashed_password
        print(f"Verifying password: {plain_password}")
        print(f"MD5 hash: {md5_hash}")
        print(f"Stored hash: {hashed_password}")
        print(f"Match result: {result}")
        return result
    except Exception as e:
        print(f"Error in password verification: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_password_hash(password: str) -> str:
    """
    Sử dụng MD5 thay vì bcrypt để đơn giản hóa quá trình phát triển
    """
    return hashlib.md5(password.encode()).hexdigest()

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Danh sách các đường dẫn không cần xác thực
PUBLIC_PATHS = [
    "/api/v1/menu-items",
    "/menu",
    "/static/",
    "/login",
]

def is_public_path(path: str) -> bool:
    """Kiểm tra xem đường dẫn có thuộc diện public không"""
    for public_path in PUBLIC_PATHS:
        if path.startswith(public_path):
            return True
    return False

def get_current_user(
    request: Request = None,
    db: Session = Depends(get_db), 
    token: Optional[str] = Cookie(None, alias="access_token"),
    header_token: Optional[str] = Depends(oauth2_scheme)
) -> Waitstaff:
    """Get current user from JWT token (either from cookie or header)"""
    # Cho phép truy cập vào các đường dẫn công khai mà không cần xác thực
    if request and is_public_path(request.url.path):
        print(f"Public path detected: {request.url.path}")
        # Nếu là GET hoặc path /menu, cho phép truy cập
        if request.method == "GET":
            print("GET request to public path, allowing access")
            return None
    
    # Ưu tiên sử dụng token từ header nếu có
    actual_token = header_token if header_token else token
    
    # Nếu không có token, trả về lỗi
    if not actual_token:
        print("No token found in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Giải mã JWT token
        payload = jwt.decode(actual_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None: 
            print("No user_id in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError as e:
        print(f"JWT error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Lấy thông tin người dùng từ database
    user = db.query(Waitstaff).filter(Waitstaff.staff_id == user_id).first()
    if user is None:
        print(f"User with ID {user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"User authenticated: {user.username} (role: {user.role})")
    return user