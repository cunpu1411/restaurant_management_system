from fastapi import Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from jose import JWTError, jwt
from app.core.config import settings

async def auth_middleware(request: Request, call_next):
    """
    Middleware xác thực token JWT từ cookie.
    Chuyển hướng về trang login nếu không có token hoặc token không hợp lệ.
    """
    try:
        # Lấy token từ cookie
        token = request.cookies.get("access_token")
        
        if not token:
            # Nếu không có token, chuyển hướng đến trang login
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
            response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            response.delete_cookie("access_token")
            return response
            
    except Exception as e:
        # Xử lý các lỗi khác
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Authentication error: {str(e)}"}
        )