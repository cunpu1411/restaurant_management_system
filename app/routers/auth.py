from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.controllers import waitstaff as waitstaff_controller
from app.core.security import create_access_token, get_current_user
from app.schemas.waitstaff import Token, Waitstaff, Login
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    response: Response,
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    print(f"Attempting OAuth2 login for user: {form_data.username}")
    waitstaff = waitstaff_controller.authenticate_waitstaff(
        db, form_data.username, form_data.password
    )
    if not waitstaff:
        print(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Authentication successful for user: {form_data.username}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        waitstaff.staff_id, expires_delta=access_token_expires
    )
    
    # Lưu token vào cookie
    response.set_cookie(
        key="access_token", 
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"  # Để đảm bảo cookie được gửi khi chuyển hướng từ trang khác
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login/json", response_model=Token)
def login_json(
    response: Response,
    login: Login, 
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON login endpoint
    """
    print(f"Attempting JSON login for user: {login.username}")
    waitstaff = waitstaff_controller.authenticate_waitstaff(
        db, login.username, login.password
    )
    if not waitstaff:
        print(f"Authentication failed for user: {login.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    print(f"Authentication successful for user: {login.username}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        waitstaff.staff_id, expires_delta=access_token_expires
    )
    
    # Lưu token vào cookie với các tùy chọn an toàn
    response.set_cookie(
        key="access_token", 
        value=access_token,
        httponly=True,  # Ngăn JavaScript truy cập cookie
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",  # Đảm bảo cookie được gửi khi chuyển hướng
        secure=False,  # Đặt True trong môi trường production với HTTPS
        path="/"  # Đảm bảo cookie có sẵn trên toàn bộ trang web
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/test-token", response_model=Waitstaff)
def test_token(
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Test access token
    """
    return current_user

@router.get("/user-info", response_model=Waitstaff)
def get_user_info(
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get current user information
    """
    return current_user