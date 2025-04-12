# app/middleware/auth.py
from fastapi import Request, status
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from app.core.config import settings

async def auth_middleware(request: Request, call_next):
    # Các đường dẫn được miễn xác thực
    exempt_routes = [
        "/login", 
        "/static", 
        "/api/v1/auth/login", 
        "/api/v1/auth/login/json"
    ]
    
    # Kiểm tra nếu đường dẫn hiện tại được miễn xác thực
    for route in exempt_routes:
        if request.url.path.startswith(route):
            return await call_next(request)
    
    # Lấy token từ cookie
    token = request.cookies.get("access_token")
    
    if not token:
        # Nếu không có token và đang truy cập trang bảo vệ, chuyển hướng đến trang login
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Xác thực token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Token hợp lệ, lưu user_id vào request state
        request.state.user_id = payload.get("sub")
        return await call_next(request)
    except JWTError:
        # Token không hợp lệ, chuyển hướng đến trang login
        response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("access_token")
        return response