from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.schemas.order import OrderCreate, OrderUpdate
from app.controllers import order_item as order_item_controller

def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.order_id == order_id).first()

def get_orders(
    db: Session, skip: int = 0, limit: int = 100, 
    status: Optional[str] = None, customer_id: Optional[int] = None,
    table_id: Optional[int] = None, waiter_id: Optional[int] = None
) -> List[Order]:
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if table_id:
        query = query.filter(Order.table_id == table_id)
    if waiter_id:
        query = query.filter(Order.waiter_id == waiter_id)
        
    return query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()

def calculate_order_total(db: Session, order_id: int) -> Decimal:
    """Calculate the total amount for an order based on its items"""
    total = Decimal('0.00')
    
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    for item in order_items:
        menu_item = db.query(MenuItem).filter(MenuItem.menu_item_id == item.menu_item_id).first()
        if menu_item:
            total += menu_item.price * Decimal(item.quantity)
            
    return total

def create_order(db: Session, order: OrderCreate) -> Order:
    # Create the order
    db_order = Order(
        customer_id=order.customer_id,
        table_id=order.table_id,
        waiter_id=order.waiter_id,
        status=order.status,
        total_amount=Decimal('0.00')  # Will be calculated after adding items
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items if provided
    if order.order_items:
        for item in order.order_items:
            order_item = OrderItem(
                order_id=db_order.order_id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                special_request=item.special_request,
                status=item.status
            )
            db.add(order_item)
        
        db.commit()
        
        # Calculate and update the total amount
        db_order.total_amount = calculate_order_total(db, db_order.order_id)
        db.commit()
        db.refresh(db_order)
    
    return db_order

def update_order(
    db: Session, order_id: int, order: OrderUpdate
) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        
        # Recalculate total if needed
        if 'total_amount' not in update_data:
            db_order.total_amount = calculate_order_total(db, order_id)
            
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if db_order:
        # Delete associated order items (should be handled by cascade)
        db.delete(db_order)
        db.commit()
        return db_order
    return None

def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
    """Update just the status of an order"""
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order