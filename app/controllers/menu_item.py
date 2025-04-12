from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session

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
        for field, value in update_data.items():
            setattr(db_menu_item, field, value)
        db.commit()
        db.refresh(db_menu_item)
    return db_menu_item

def delete_menu_item(db: Session, menu_item_id: int) -> Optional[MenuItem]:
    db_menu_item = get_menu_item(db, menu_item_id)
    if db_menu_item:
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