from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
import os
from pathlib import Path

from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate

def get_menu_item(db: Session, menu_item_id: int) -> Optional[MenuItem]:
    return db.query(MenuItem).filter(MenuItem.menu_item_id == menu_item_id).first()

def get_menu_items(
    db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None
) -> List[MenuItem]:
    if category_id:
        return db.query(MenuItem).filter(MenuItem.category_id == category_id).offset(skip).limit(limit).all()
    return db.query(MenuItem).offset(skip).limit(limit).all()

def get_available_menu_items(
    db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None
) -> List[MenuItem]:
    query = db.query(MenuItem).filter(MenuItem.is_available == True)
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    return query.offset(skip).limit(limit).all()

def create_menu_item(db: Session, menu_item: MenuItemCreate) -> MenuItem:
    db_menu_item = MenuItem(
        category_id=menu_item.category_id,
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
        is_available=menu_item.is_available,
        image_url=menu_item.image_url if hasattr(menu_item, 'image_url') else None
    )
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

def update_menu_item(
    db: Session, menu_item_id: int, menu_item: MenuItemUpdate
) -> Optional[MenuItem]:
    db_menu_item = get_menu_item(db, menu_item_id)
    if db_menu_item:
        update_data = menu_item.dict(exclude_unset=True)
        
        # If we're updating the image and there's an existing image, delete the old file
        if 'image_url' in update_data and db_menu_item.image_url:
            try:
                # Get the filename from the URL
                old_filename = os.path.basename(db_menu_item.image_url)
                old_file_path = Path("app/static/images") / old_filename
                
                # Check if the file exists before attempting to delete
                if old_file_path.exists() and old_file_path.is_file():
                    os.remove(old_file_path)
            except Exception as e:
                # Log the error but continue with the update
                print(f"Error deleting old image file: {e}")
                
        # Update the menu item with the new data
        for field, value in update_data.items():
            setattr(db_menu_item, field, value)
            
        db.commit()
        db.refresh(db_menu_item)
    return db_menu_item

def delete_menu_item(db: Session, menu_item_id: int) -> Optional[MenuItem]:
    db_menu_item = get_menu_item(db, menu_item_id)
    if db_menu_item:
        # Delete the associated image file if it exists
        if db_menu_item.image_url:
            try:
                # Get the filename from the URL
                filename = os.path.basename(db_menu_item.image_url)
                file_path = Path("app/static/images") / filename
                
                # Check if the file exists before attempting to delete
                if file_path.exists() and file_path.is_file():
                    os.remove(file_path)
            except Exception as e:
                # Log the error but continue with the deletion
                print(f"Error deleting image file: {e}")
                
        db.delete(db_menu_item)
        db.commit()
        return db_menu_item
    return None

def toggle_availability(db: Session, menu_item_id: int) -> Optional[MenuItem]:
    db_menu_item = get_menu_item(db, menu_item_id)
    if db_menu_item:
        db_menu_item.is_available = not db_menu_item.is_available
        db.commit()
        db.refresh(db_menu_item)
    return db_menu_item