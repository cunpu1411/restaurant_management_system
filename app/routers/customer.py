from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import customer as customer_controller
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[Customer])
def read_customers(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Retrieve customers.
    """
    customers = customer_controller.get_customers(db, skip=skip, limit=limit)
    return customers

@router.post("/", response_model=Customer)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: CustomerCreate,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Create new customer.
    """
    # Check if customer with the same contact number already exists
    if customer_in.contact_number:
        existing_customer = customer_controller.get_customer_by_contact(
            db, contact_number=customer_in.contact_number
        )
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this contact number already exists"
            )
    
    # Create the customer
    return customer_controller.create_customer(db, customer=customer_in)

@router.get("/{customer_id}", response_model=Customer)
def read_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Get customer by ID.
    """
    customer = customer_controller.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: CustomerUpdate,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Update a customer.
    """
    customer = customer_controller.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
        
    # Check if updating to an existing contact number
    if customer_in.contact_number and customer_in.contact_number != customer.contact_number:
        existing_customer = customer_controller.get_customer_by_contact(
            db, contact_number=customer_in.contact_number
        )
        if existing_customer and existing_customer.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this contact number already exists"
            )
    
    return customer_controller.update_customer(db, customer_id=customer_id, customer=customer_in)

@router.delete("/{customer_id}", response_model=Customer)
def delete_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Delete a customer.
    """
    # Only managers can delete customers
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    customer = customer_controller.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer_controller.delete_customer(db, customer_id=customer_id)

@router.post("/get-or-create", response_model=Customer)
def get_or_create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: CustomerCreate,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Get an existing customer by contact number or create a new one.
    """
    return customer_controller.get_or_create_customer(db, customer=customer_in)