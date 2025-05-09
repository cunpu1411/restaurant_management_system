from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.config import settings
from app.routers import api_router
from app.routers import __init__
from app.middleware.auth import auth_middleware
from app.core.database import get_db
from app.controllers import waitstaff as waitstaff_controller
from app.controllers import menu_item as menu_item_controller
from app.controllers import table as table_controller
from app.controllers import category as category_controller
from app.controllers import order as order_controller
from app.controllers import customer as customer_controller
from app.schemas.customer import CustomerCreate
from app.schemas.order import OrderCreate
from app.schemas.order import OrderItemCreate
from app.core.security import create_access_token
from app.models.waitstaff import Waitstaff

import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Thêm middleware xác thực
@app.middleware("http")
async def add_auth_middleware(request: Request, call_next):
    try:
        print(f"Processing request: {request.url.path}")
        return await auth_middleware(request, call_next)
    except Exception as e:
        print(f"Error in auth middleware: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Nếu main.py nằm trong app/
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

def escapejs_filter(value):
    """Escape chuỗi giá trị để an toàn với JavaScript"""
    if value is None:
        return ""
    value = str(value)
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    value = value.replace("'", "\\'")
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('\t', '\\t')
    return value

# Đăng ký filter với Jinja2
templates.env.filters["escapejs"] = escapejs_filter

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Frontend routes
@app.get("/")
async def root(request: Request):
    print("Root route accessed")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    print("Login page accessed directly")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_process(request: Request, db: Session = Depends(get_db)):
    try:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        
        print(f"Login attempt for user: {username}")
        
        # Xác thực người dùng
        user = waitstaff_controller.authenticate_waitstaff(db, username, password)
        if not user:
            print("Authentication failed")
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Incorrect username or password"
            })
        
        print(f"User authenticated: {user.name}")
        
        # Tạo token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.staff_id, expires_delta=access_token_expires)
        
        # Tạo response với chuyển hướng
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        # Lưu token vào cookie
        response.set_cookie(
            key="access_token", 
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        return response
    except Exception as e:
        print(f"Error in login_process: {str(e)}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"Login error: {str(e)}"
        })

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

# Thêm route này để bypass đăng nhập
@app.get("/admin-login")
async def admin_login(response: Response, db: Session = Depends(get_db)):
    """Temporary admin login bypass"""
    try:
        # Lấy admin user từ database - sửa lại tên class
        admin = db.query(Waitstaff).filter(Waitstaff.username == "admin").first()
        if not admin:
            print("Admin user not found")
            return {"error": "Admin user not found in database"}
            
        print(f"Admin login bypass for user: {admin.username}")
        
        # Tạo token cho admin
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(admin.staff_id, expires_delta=access_token_expires)
        
        # Lưu token vào cookie
        response.set_cookie(
            key="access_token", 
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        # Chuyển hướng đến dashboard
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        print(f"Error in admin_login: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Admin login error: {str(e)}"}
        )

@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        # Lấy thông tin user từ token
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        print(f"Dashboard accessed by user_id: {user_id}")
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user_id": user_id
        })
    except Exception as e:
        print(f"Error in dashboard: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Dashboard error: {str(e)}"}
        )

@app.get("/orders")
async def orders(request: Request):
    try:
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        print(f"Orders accessed by user_id: {user_id}")
        return templates.TemplateResponse("orders.html", {"request": request})
    except Exception as e:
        print(f"Error in orders: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/menu")
async def menu(request: Request, db: Session = Depends(get_db)):
    try:
        # Lấy thông tin user từ token
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        print(f"Menu accessed by user_id: {user_id}")
        
        # Lấy dữ liệu categories và menu items
        categories = category_controller.get_categories(db)
        menu_items = menu_item_controller.get_menu_items(db)
        
        print(f"Categories loaded: {len(categories)}")
        print(f"Menu items loaded: {len(menu_items)}")
        
        return templates.TemplateResponse(
            "menu.html", 
            {
                "request": request,
                "categories": categories,
                "menu_items": menu_items
            }
        )
    except Exception as e:
        print(f"Error in menu route: {str(e)}")
        # Thay vì chuyển hướng, hiển thị trang lỗi
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request,
                "error": str(e)
            }
        )

@app.get("/tables")
async def tables(request: Request):
    try:
        return templates.TemplateResponse("tables.html", {"request": request})
    except Exception as e:
        print(f"Error in tables: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )

@app.get("/customers")
async def customers(request: Request):
    try:
        return templates.TemplateResponse("customers.html", {"request": request})
    except Exception as e:
        print(f"Error in customers: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )

# Add simple test route
@app.get("/test")
async def test():
    return {"message": "API is working!"}

# Thêm route cho trang đặt món của khách hàng
@app.get("/order")
async def customer_order_page(request: Request, db: Session = Depends(get_db)):
    """
    Trang công khai cho khách hàng đặt món không cần đăng nhập
    """
    try:
        # Lấy dữ liệu categories và menu items
        categories = category_controller.get_categories(db)
        menu_items = menu_item_controller.get_available_menu_items(db)
        tables = table_controller.get_tables(db)
        
        print("Rendering customer order page")
        print(f"Categories loaded: {len(categories)}")
        print(f"Available menu items loaded: {len(menu_items)}")
        print(f"Tables loaded: {len(tables)}")
        
        return templates.TemplateResponse(
            "customer_order.html", 
            {
                "request": request,
                "categories": categories,
                "menu_items": menu_items,
                "tables": tables
            }
        )
    except Exception as e:
        print(f"Error in customer order page: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request,
                "error": str(e)
            }
        )

# Thêm API endpoint để xử lý đơn hàng từ khách hàng
@app.post("/api/v1/customer/orders")
async def create_customer_order(
    order_data: dict,
    db: Session = Depends(get_db)
):
    """
    API để xử lý đơn hàng từ trang đặt món của khách hàng
    """
    try:
        print("Processing customer order")
        print(f"Order data: {order_data}")
        
        # Xử lý thông tin khách hàng
        customer_data = CustomerCreate(
            name=order_data.get("customer", {}).get("name", ""),
            contact_number=order_data.get("customer", {}).get("contact_number", "")
        )
        
        # Tìm hoặc tạo mới khách hàng
        customer = customer_controller.get_or_create_customer(db, customer=customer_data)
        
        # Xây dựng order items
        order_items = []
        for item in order_data.get("order_items", []):
            order_item = OrderItemCreate(
                menu_item_id=item.get("menu_item_id"),
                quantity=item.get("quantity", 1),
                special_request=item.get("special_request", ""),
                status="pending"
            )
            order_items.append(order_item)
        
        # Tạo order mới
        order_create = OrderCreate(
            customer_id=customer.customer_id,
            table_id=order_data.get("table_id"),
            status="pending",
            order_items=order_items
        )
        
        # Tạo đơn hàng mới
        new_order = order_controller.create_order(db, order=order_create)
        
        print(f"Order created successfully with ID: {new_order.order_id}")
        
        return {
            "status": "success",
            "message": "Đơn hàng đã được tạo thành công",
            "order_id": new_order.order_id
        }
        
    except Exception as e:
        print(f"Error creating customer order: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Lỗi khi tạo đơn hàng: {str(e)}"}
        )

#Thêm route cho staff pagepage
@app.get("/staff")
async def staff(request: Request, db: Session = Depends(get_db)):
    try:
        # Lấy thông tin user từ token
        user_id = request.state.user_id if hasattr(request.state, "user_id") else None
        print(f"Staff page accessed by user_id: {user_id}")
        
        return templates.TemplateResponse("staff.html", {
            "request": request,
            "user_id": user_id
        })
    except Exception as e:
        print(f"Error in staff: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, debug=True)