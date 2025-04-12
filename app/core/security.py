from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
import bcrypt
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.waitstaff import Waitstaff
from app.core.database import get_db

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

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

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Waitstaff:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None: 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(Waitstaff).filter(Waitstaff.staff_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user