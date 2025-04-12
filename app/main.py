from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.config import settings
from app.routers import api_router
from app.middleware.auth import auth_middleware
from app.core.database import get_db
from app.controllers import waitstaff as waitstaff_controller
from app.core.security import create_access_token
from app.models.waitstaff import Waitstaff
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
    return await auth_middleware(request, call_next)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Frontend routes
@app.get("/")
async def root():
    # Chuyển hướng đến dashboard
    return RedirectResponse(url="/login")

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_process(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    # Xác thực người dùng
    user = waitstaff_controller.authenticate_waitstaff(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect username or password"
        })
    
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
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

# Thêm route này để bypass đăng nhập
@app.get("/admin-login")
async def admin_login(response: Response, db: Session = Depends(get_db)):
    """Temporary admin login bypass"""
    # Lấy admin user từ database
    admin = db.query(waitstaff).filter(waitstaff.username == "admin").first()
    if not admin:
        return {"error": "Admin user not found in database"}
        
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

@app.get("/dashboard")
async def dashboard(request: Request):
    # Lấy thông tin user từ token
    user_id = request.state.user_id if hasattr(request.state, "user_id") else None
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/orders")
async def orders(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})

@app.get("/menu")
async def menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

@app.get("/tables")
async def tables(request: Request):
    return templates.TemplateResponse("tables.html", {"request": request})

@app.get("/customers")
async def customers(request: Request):
    return templates.TemplateResponse("customers.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)