from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import waitstaff as waitstaff_controller
from app.schemas.waitstaff import Waitstaff, WaitstaffCreate, WaitstaffUpdate
from app.schemas.waitstaff import Waitstaff as WaitstaffSchema

router = APIRouter()

@router.get("/", response_model=List[WaitstaffSchema])
def read_waitstaff(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve waitstaff.
    """
    # Only managers can view all waitstaff
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    waitstaff = waitstaff_controller.get_waitstaffs(db, skip=skip, limit=limit)
    return waitstaff

@router.post("/", response_model=WaitstaffSchema)
def create_waitstaff(
    *,
    db: Session = Depends(get_db),
    waitstaff_in: WaitstaffCreate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Create new waitstaff.
    """
    # Only managers can create waitstaff
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    # Check if waitstaff with the same username already exists
    existing_waitstaff = waitstaff_controller.get_waitstaff_by_username(
        db, username=waitstaff_in.username
    )
    if existing_waitstaff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )
    
    # Create the waitstaff
    return waitstaff_controller.create_waitstaff(db, waitstaff=waitstaff_in)

@router.get("/me", response_model=WaitstaffSchema)
def read_waitstaff_me(
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get current waitstaff.
    """
    return current_user

@router.get("/{staff_id}", response_model=WaitstaffSchema)
def read_waitstaff_by_id(
    *,
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get waitstaff by ID.
    """
    # Staff can view their own profile, managers can view all
    if current_user.staff_id != staff_id and current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    waitstaff = waitstaff_controller.get_waitstaff(db, staff_id=staff_id)
    if not waitstaff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitstaff not found"
        )
    return waitstaff

@router.put("/{staff_id}", response_model=WaitstaffSchema)
def update_waitstaff(
    *,
    staff_id: int,
    waitstaff_in: WaitstaffUpdate,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update waitstaff.
    """
    # Staff can update their own profile, managers can update all
    # But only managers can change roles
    if current_user.staff_id != staff_id and current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    if waitstaff_in.role and current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can change roles"
        )
        
    waitstaff = waitstaff_controller.get_waitstaff(db, staff_id=staff_id)
    if not waitstaff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitstaff not found"
        )
        
    # Check if updating to an existing username
    if waitstaff_in.username and waitstaff_in.username != waitstaff.username:
        existing_waitstaff = waitstaff_controller.get_waitstaff_by_username(
            db, username=waitstaff_in.username
        )
        if existing_waitstaff and existing_waitstaff.staff_id != staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists"
            )
    
    return waitstaff_controller.update_waitstaff(db, staff_id=staff_id, waitstaff=waitstaff_in)

@router.delete("/{staff_id}", response_model=WaitstaffSchema)
def delete_waitstaff(
    *,
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete waitstaff.
    """
    # Only managers can delete waitstaff
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    # Cannot delete yourself
    if current_user.staff_id == staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
        
    waitstaff = waitstaff_controller.get_waitstaff(db, staff_id=staff_id)
    if not waitstaff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitstaff not found"
        )
    return waitstaff_controller.delete_waitstaff(db, staff_id=staff_id)