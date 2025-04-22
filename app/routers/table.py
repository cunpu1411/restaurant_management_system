from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import table as table_controller
from app.schemas.table import Table, TableCreate, TableUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[Table])
def read_tables(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Optional[Waitstaff] = Depends(get_current_user)  # Làm thành Optional
) -> Any:
    """
    Retrieve tables.
    """
    # Bỏ phần kiểm tra current_user
    tables = table_controller.get_tables(db, skip=skip, limit=limit)
    return tables

@router.post("/", response_model=Table)
def create_table(
    *,
    db: Session = Depends(get_db),
    table_in: TableCreate,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Create new table.
    """
    # Kiểm tra quyền chỉ khi có current_user
    if current_user and current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    # Check if table with the same number already exists
    existing_table = table_controller.get_table_by_number(
        db, table_number=table_in.table_number
    )
    if existing_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Table with this number already exists"
        )
    
    # Create the table
    return table_controller.create_table(db, table=table_in)

@router.get("/{table_id}", response_model=Table)
def read_table(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Get table by ID.
    """
    table = table_controller.get_table(db, table_id=table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    return table

@router.put("/{table_id}", response_model=Table)
def update_table(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    table_in: TableUpdate,
    current_user: Optional[Waitstaff] = Depends(get_current_user)
) -> Any:
    """
    Update a table.
    """
    # Check permission if current_user exists
    if current_user and current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    table = table_controller.get_table(db, table_id=table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
        
    # Check if updating to an existing table number
    if table_in.table_number and table_in.table_number != table.table_number:
        existing_table = table_controller.get_table_by_number(
            db, table_number=table_in.table_number
        )
        if existing_table and existing_table.table_id != table_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table with this number already exists"
            )
    
    return table_controller.update_table(db, table_id=table_id, table=table_in)

# In the delete_table function, change the Optional[Waitstaff] to require authentication
@router.delete("/{table_id}", response_model=Table)
def delete_table(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    current_user: Waitstaff = Depends(get_current_user)  # Remove Optional[]
) -> Any:
    """
    Delete a table.
    """
    # Only managers can delete tables
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    table = table_controller.get_table(db, table_id=table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    return table_controller.delete_table(db, table_id=table_id)