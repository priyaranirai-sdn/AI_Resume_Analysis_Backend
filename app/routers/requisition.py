from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.models.database import get_db
from app.models.requisition import Requisition
from app.models.user import User
from app.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/requisition", tags=["Requisition"])

class RequisitionCreate(BaseModel):
    title: str
    department: str
    location: str
    experience_required: int
    skills_required: List[str]
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    employment_type: str = "Full-time"

class RequisitionUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[int] = None
    skills_required: Optional[List[str]] = None
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None

class RequisitionResponse(BaseModel):
    id: int
    title: str
    department: str
    location: str
    experience_required: int
    skills_required: List[str]
    responsibilities: Optional[str]
    qualifications: Optional[str]
    salary_range_min: Optional[int]
    salary_range_max: Optional[int]
    employment_type: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=RequisitionResponse)
def create_requisition(
    requisition: RequisitionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job requisition"""
    db_requisition = Requisition(
        **requisition.dict(),
        created_by=current_user.id
    )
    db.add(db_requisition)
    db.commit()
    db.refresh(db_requisition)
    return db_requisition

@router.get("/", response_model=List[RequisitionResponse])
def get_requisitions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all requisitions for the current user"""
    requisitions = db.query(Requisition).filter(
        Requisition.created_by == current_user.id
    ).offset(skip).limit(limit).all()
    return requisitions

@router.get("/{requisition_id}", response_model=RequisitionResponse)
def get_requisition(
    requisition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific requisition by ID"""
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    return requisition

@router.put("/{requisition_id}", response_model=RequisitionResponse)
def update_requisition(
    requisition_id: int,
    requisition_update: RequisitionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a requisition"""
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    # Update only provided fields
    update_data = requisition_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(requisition, field, value)
    
    requisition.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(requisition)
    
    return requisition

@router.delete("/{requisition_id}")
def delete_requisition(
    requisition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a requisition"""
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    db.delete(requisition)
    db.commit()
    
    return {"message": "Requisition deleted successfully"}
