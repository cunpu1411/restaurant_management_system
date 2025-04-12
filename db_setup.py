import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import hashlib

# Thêm thư mục hiện tại và thư mục cha vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Import all models to create tables
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.customer import Customer
from app.models.waitstaff import Waitstaff
from app.models.table import Table
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.feedback import Feedback

from app.core.config import settings
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Tung%4015436902@localhost/restaurant_management")

# Create database engine
engine = create_engine(DATABASE_URL)

# Create base
Base = declarative_base()

# Import models to ensure they're part of the metadata
from app.core.database import Base

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Initialize database with default data
def init_db():
    try:
        # Xóa admin cũ nếu có
        admin = db.query(Waitstaff).filter(Waitstaff.username == "admin").first()
        if admin:
            logger.info("Đang xóa admin cũ...")
            db.delete(admin)
            db.commit()

        # Tạo admin mới
        logger.info("Đang tạo admin mới...")
        admin_password = "admin123"
        
        # Sử dụng MD5 hash cho mật khẩu
        password_hash = hashlib.md5(admin_password.encode()).hexdigest()
        logger.info(f"Mật khẩu hash: {password_hash}")
        
        admin = Waitstaff(
            name="Admin",
            role="Manager",
            contact_number="123456789",
            username="admin",
            password_hash=password_hash
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        logger.info(f"Admin ID: {admin.staff_id}")
        logger.info(f"Admin username: {admin.username}")
        logger.info(f"Admin password_hash: {admin.password_hash}")
            
        # Check if categories exist
        categories = db.query(Category).count()
        if categories == 0:
            logger.info("Creating default categories")
            for category_name in ["Main Course", "Appetizers", "Desserts", "Beverages"]:
                category = Category(name=category_name)
                db.add(category)
            db.commit()
            
        # Check if tables exist
        tables = db.query(Table).count()
        if tables == 0:
            logger.info("Creating default tables")
            for i in range(1, 11):  # Create 10 tables
                table = Table(table_number=f"T{i}", capacity=4)
                db.add(table)
            db.commit()
            
        # Check if menu items exist
        menu_items = db.query(MenuItem).count()
        if menu_items == 0:
            logger.info("Creating sample menu items")
            # Get category IDs
            main_course = db.query(Category).filter(Category.name == "Main Course").first()
            appetizer = db.query(Category).filter(Category.name == "Appetizers").first()
            dessert = db.query(Category).filter(Category.name == "Desserts").first()
            beverage = db.query(Category).filter(Category.name == "Beverages").first()
            
            # Sample menu items
            items = [
                MenuItem(category_id=main_course.category_id, name="Grilled Salmon", description="Fresh salmon with herbs", price=18.99, is_available=True),
                MenuItem(category_id=main_course.category_id, name="Beef Steak", description="Premium cut with sauce", price=22.99, is_available=True),
                MenuItem(category_id=appetizer.category_id, name="Cheese Platter", description="Selection of cheeses", price=10.99, is_available=True),
                MenuItem(category_id=dessert.category_id, name="Chocolate Cake", description="Rich chocolate cake", price=7.99, is_available=True),
                MenuItem(category_id=beverage.category_id, name="Fresh Orange Juice", description="Freshly squeezed", price=4.99, is_available=True),
            ]
            
            for item in items:
                db.add(item)
            db.commit()
            
        logger.info("Database initialized")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")