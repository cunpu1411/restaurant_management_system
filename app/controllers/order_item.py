from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.order_item import OrderItem
from app.schemas.order_item import OrderItemCreate, OrderItemUpdate

def get_order_item(db: Session, order_item_id: int) -> Optional[OrderItem]:
    return db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()

def get_order_items_by_order(
    db: Session, order_id: int, skip: int = 0, limit: int = 100
) -> List[OrderItem]:
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).offset(skip).limit(limit).all()

def create_order_item(db: Session, order_item: OrderItemCreate) -> OrderItem:
    db_order_item = OrderItem(
        order_id=order_item.order_id,
        menu_item_id=order_item.menu_item_id,
        quantity=order_item.quantity,
        special_request=order_item.special_request,
        status=order_item.status,
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

def update_order_item(
    db: Session, order_item_id: int, order_item: OrderItemUpdate
) -> Optional[OrderItem]:
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item:
        update_data = order_item.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order_item, field, value)
        db.commit()
        db.refresh(db_order_item)
    return db_order_item

def delete_order_item(db: Session, order_item_id: int) -> Optional[OrderItem]:
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item:
        db.delete(db_order_item)
        db.commit()
        return db_order_item
    return None

def update_order_item_status(db: Session, order_item_id: int, status: str) -> Optional[OrderItem]:
    """Update just the status of an order item"""
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item:
        db_order_item.status = status
        db.commit()
        db.refresh(db_order_item)
    return db_order_item

def batch_update_status(db: Session, order_id: int, status: str) -> List[OrderItem]:
    """Update the status of all items in an order"""
    db_order_items = get_order_items_by_order(db, order_id)
    
    for item in db_order_items:
        item.status = status
    
    db.commit()
    return db_order_items