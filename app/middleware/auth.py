from fastapi import Request, status, HTTPException
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
    
    # Routes that should be accessible after login
    authenticated_routes = [
        '/dashboard', 
        '/menu', 
        '/orders', 
        '/tables', 
        '/customers', 
        '/api/v1/menu-items',
        '/api/v1/categories'
    ]
    
    print(f"Auth Middleware: Processing route {request.url.path}")
    print(f"Request method: {request.method}")
    
    # Public routes bypass authentication
    if any(request.url.path.startswith(route) for route in public_routes):
        print(f"Route {request.url.path} is public, bypassing authentication")
        return await call_next(request)
    
    try:
        # Lấy token từ cookie
        token = request.cookies.get("access_token")
        
        if not token:
            print(f"No token for route: {request.url.path}")
            # For API routes, return 401
            if any(request.url.path.startswith(route) for route in ['/api/v1']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Authentication required"
                )
            # For page routes, redirect to login
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
        try:
            # Xác thực token
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            # Token hợp lệ, lưu user_id vào request state
            request.state.user_id = payload.get("sub")
            
            print(f"Token validated for user: {request.state.user_id}")
            
            # Cho phép truy cập các route đã xác thực
            if any(request.url.path.startswith(route) for route in authenticated_routes):
                return await call_next(request)
            
            print(f"Unauthorized access attempt to: {request.url.path}")
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            
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