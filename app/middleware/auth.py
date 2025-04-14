from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from jose import JWTError, jwt
from app.core.config import settings

async def auth_middleware(request: Request, call_next):
    """
    Middleware xác thực token JWT từ cookie.
    Cho phép truy cập các route public
    """
    # Danh sách các route không yêu cầu xác thực
    public_routes = ['/login', '/admin-login', '/static', '/test', '/', '']
    
    # Bỏ qua xác thực cho các route public
    if any(request.url.path.startswith(route) for route in public_routes):
        return await call_next(request)
    
    try:
        # Lấy token từ cookie
        token = request.cookies.get("access_token")
        
        if not token:
            # Nếu không có token và không phải route public, chuyển hướng đến login
            print(f"No token for route: {request.url.path}")
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
        try:
            # Xác thực token
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            # Token hợp lệ, lưu user_id vào request state
            request.state.user_id = payload.get("sub")
            
            # Tiếp tục xử lý request
            return await call_next(request)
            
        except JWTError:
            # Token không hợp lệ, xóa token khỏi cookie và chuyển hướng đến trang login
            print(f"Invalid token for route: {request.url.path}")
            response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            response.delete_cookie("access_token")
            return response
            
    except Exception as e:
        # Xử lý các lỗi khác
        print(f"Authentication error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Authentication error: {str(e)}"}
        )