from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()

def get_customer_by_contact(db: Session, contact_number: str) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.contact_number == contact_number).first()

def get_customers(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Customer]:
    return db.query(Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    db_customer = Customer(
        name=customer.name,
        contact_number=customer.contact_number,
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(
    db: Session, customer_id: int, customer: CustomerUpdate
) -> Optional[Customer]:
    db_customer = get_customer(db, customer_id)
    if db_customer:
        update_data = customer.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int) -> Optional[Customer]:
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
        return db_customer
    return None

def get_or_create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """Get existing customer by contact number or create a new one"""
    if customer.contact_number:
        db_customer = get_customer_by_contact(db, customer.contact_number)
        if db_customer:
            # Update the name if provided and different
            if customer.name and customer.name != db_customer.name:
                db_customer.name = customer.name
                db.commit()
                db.refresh(db_customer)
            return db_customer
    
    # Create new customer
    return create_customer(db, customer)