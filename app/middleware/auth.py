from fastapi import Request, status, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from jose import JWTError, jwt
from app.core.config import settings
from app.models.waitstaff import Waitstaff
from app.core.database import SessionLocal

async def auth_middleware(request: Request, call_next):
    """
    Middleware xác thực token JWT từ cookie.
    Cho phép truy cập các route public
    """
    # Danh sách các route không yêu cầu xác thực
    public_routes = [
    '/login', 
    '/admin-login', 
    '/static', 
    '/test', 
    '/', 
    '',
    '/api/v1/auth/login',
    '/api/v1/auth/login/json',
    '/favicon.ico',
    '/menu',
    '/order',
    '/tables',
    '/api/v1/tables',
    '/api/v1/tables/'
    ]
    
    # Routes API công khai cho các thao tác GET
    public_api_routes = [
        '/api/v1/menu-items',
        '/api/v1/categories',
        '/api/v1/customer/orders',
        '/api/v1/dashboard/stats',
        '/api/v1/tables',
        '/api/v1/tables/',
        '/api/v1/waitstaff',
        '/api/v1/customers',
        '/api/v1/orders'
    ]

    # Routes that Waiters are allowed to access
    waiter_allowed_routes = [
        '/menu',
        '/tables',
        '/api/v1/menu-items',
        '/api/v1/menu-items/',
        '/api/v1/tables',
        '/api/v1/tables/'
    ]
    
    # Routes that should be accessible after login
    authenticated_routes = [
        '/dashboard', 
        '/menu', 
        '/orders', 
        '/tables', 
        '/customers',
    ]
    
    print(f"Auth Middleware: Processing route {request.url.path}")
    print(f"Request method: {request.method}")
    
    # Public routes bypass authentication
    if any(request.url.path.startswith(route) for route in public_routes):
        print(f"Route {request.url.path} is public, bypassing authentication")
        return await call_next(request)
    
    # Cho phép truy cập GET request tới các API công khai
    if request.method == "GET" and any(request.url.path.startswith(route) for route in public_api_routes):
        print(f"GET request to public API route {request.url.path}, bypassing authentication")
        return await call_next(request)
    
    # Xử lý đặc biệt cho các request GET đến một menu item cụ thể
    if request.method == "GET" and request.url.path.startswith('/api/v1/menu-items/') and request.url.path.count('/') == 4:
        print(f"GET request to specific menu item {request.url.path}, bypassing authentication")
        return await call_next(request)
    
    try:
        # Lấy token từ cookie hoặc từ header Authorization
        token = request.cookies.get("access_token")
        
        # Nếu không có trong cookie, kiểm tra trong header
        if not token and "authorization" in request.headers:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix
                print("Found token in Authorization header")
        
        if not token:
            print(f"No token for route: {request.url.path}")
            # For API routes, return 401
            if request.url.path.startswith('/api/v1'):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    content={"detail": "Not authenticated"}
                )
            # For page routes, redirect to login
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
        try:
            # Xác thực token
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            # Token hợp lệ, lưu user_id vào request state
            user_id = payload.get("sub")
            request.state.user_id = user_id
            
            print(f"Token validated for user_id: {user_id}")

            # Check if the user is a Waiter and restrict access
            db = SessionLocal()
            try:
                user = db.query(Waitstaff).filter(Waitstaff.staff_id == user_id).first()
                
                # If user is a Waiter, check if they're accessing allowed routes
                if user and user.role == "Waiter":
                    is_allowed = False
                    
                    # Check if the route is allowed for waiters
                    for route in waiter_allowed_routes:
                        if request.url.path.startswith(route):
                            is_allowed = True
                            break
                    
                    # If not allowed, return 403 Forbidden
                    if not is_allowed:
                        print(f"Waiter {user.username} attempted to access restricted route: {request.url.path}")
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "Not enough permissions to access this page"}
                        )
            except Exception as e:
                print(f"Error checking waiter permissions: {str(e)}")
            finally:
                db.close()
            
            # Kiểm tra quyền hạn cho các API thay đổi dữ liệu menu
            if (request.url.path.startswith('/api/v1/menu-items') and 
                request.method in ["PUT", "POST", "DELETE"]):
                
                # Kiểm tra xem người dùng có quyền Manager hay không
                db = SessionLocal()
                try:
                    user = db.query(Waitstaff).filter(Waitstaff.staff_id == user_id).first()
                    if not user or user.role != "Manager":
                        print(f"User {user_id} is not Manager, denying access to {request.url.path}")
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "Not enough permissions"}
                        )
                    print(f"User {user_id} has Manager role, allowing {request.method} to {request.url.path}")
                except Exception as e:
                    print(f"Error checking user role: {str(e)}")
                    return JSONResponse(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"detail": f"Error checking permissions: {str(e)}"}
                    )
                finally:
                    db.close()
            
            # Cho phép truy cập các route đã xác thực
            return await call_next(request)
            
        except jwt.JWTError as e:
            # Token không hợp lệ, xóa token khỏi cookie và chuyển hướng đến trang login
            print(f"Invalid token for route: {request.url.path}, Error: {str(e)}")
            
            # Nếu là API request, trả về lỗi 401
            if request.url.path.startswith('/api/v1'):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication credentials"}
                )
            
            # Nếu là page request, chuyển hướng về trang login
            response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
            response.delete_cookie("access_token")
            return response
            
    except Exception as e:
        # Xử lý các lỗi khác
        print(f"Authentication error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Authentication error: {str(e)}"}
        )