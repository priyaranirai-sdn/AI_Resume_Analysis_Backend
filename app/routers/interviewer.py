from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr

# ---------------- Import models and DB session ----------------
from app.models.database import get_db
from app.models.interviewer import Interviewer
from app.models.user import User
from app.auth import get_current_user  # Auth dependency to get current logged-in user

# ---------------- Initialize Router ----------------
router = APIRouter(prefix="/interviewer", tags=["Interviewers"])

# ---------------- Pydantic Schemas ----------------
class TimeSlot(BaseModel):
    """
    Represents a single availability time slot for an interviewer.
    - start: string in "HH:MM" 24-hour format
    - end: string in "HH:MM" 24-hour format
    """
    start: str
    end: str

class InterviewerCreate(BaseModel):
    """
    Schema for creating or updating an interviewer.
    - emp_id: Employee ID (unique within company)
    - name: Full name
    - skills: List of skills
    - experience: Number of years
    - mobile: Unique mobile number
    - email: Unique email
    - availability: List of available time slots
    """
    emp_id: str
    name: str
    skills: List[str] = []
    experience: int = 0
    mobile: str
    email: EmailStr
    availability: List[TimeSlot] = []

class InterviewerResponse(BaseModel):
    """
    Response schema for returning interviewer data to frontend.
    - Includes emp_id, personal info, skills, availability, and timestamps
    """
    id: int
    emp_id: str
    name: str
    skills: List[str] = []
    experience: int
    mobile: str
    email: str
    availability: List[TimeSlot] = []
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Allows automatic ORM -> Pydantic conversion
    model_config = {"from_attributes": True}

class StandardResponse(BaseModel):
    """
    Standardized API response wrapper.
    - status: "success" or "error"
    - message: Human-readable message
    - data: Optional payload
    """
    status: str
    message: str
    data: dict | list | None = None

# ---------------- Create Interviewer ----------------
@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def create_interviewer(
    payload: InterviewerCreate,
    current_user: User = Depends(get_current_user),  # Get authenticated user
    db: Session = Depends(get_db)                   # Get DB session
):
    """
    Endpoint to create a new interviewer.
    - Validates uniqueness for emp_id, mobile, and email.
    - Saves availability time slots as JSON.
    """
    # Check if emp_id, mobile, or email already exists
    existing = db.query(Interviewer).filter(
        (Interviewer.emp_id == payload.emp_id) |
        (Interviewer.mobile == payload.mobile) |
        (Interviewer.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interviewer with same emp_id, mobile, or email already exists"
        )

    # Create SQLAlchemy Interviewer instance
    interviewer = Interviewer(
        emp_id=payload.emp_id,
        name=payload.name,
        skills=payload.skills,
        experience=payload.experience,
        mobile=payload.mobile,
        email=payload.email,
        # Convert list of Pydantic TimeSlot objects to JSON
        availability=[slot.dict() for slot in payload.availability],
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Add and commit to DB
    db.add(interviewer)
    db.commit()
    db.refresh(interviewer)  # Refresh to get ID and timestamps

    return StandardResponse(
        status="success",
        message="Interviewer created successfully",
        data={"interviewer": InterviewerResponse.from_orm(interviewer)}
    )

# ---------------- Get All Interviewers ----------------
@router.get("/", response_model=StandardResponse)
def get_all_interviewers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all interviewers created by the authenticated user.
    Returns a list of InterviewerResponse objects.
    """
    interviewers = db.query(Interviewer).filter(
        Interviewer.created_by == current_user.id
    ).all()
    interviewer_list = [InterviewerResponse.from_orm(i) for i in interviewers]

    return StandardResponse(
        status="success",
        message=f"{len(interviewer_list)} interviewer(s) retrieved successfully",
        data={"interviewers": interviewer_list}
    )

# ---------------- Get Single Interviewer ----------------
@router.get("/{interviewer_id}", response_model=StandardResponse)
def get_interviewer(
    interviewer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a single interviewer by ID.
    Only accessible by the creator.
    """
    interviewer = db.query(Interviewer).filter(
        Interviewer.id == interviewer_id,
        Interviewer.created_by == current_user.id
    ).first()

    if not interviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interviewer not found"
        )

    return StandardResponse(
        status="success",
        message="Interviewer retrieved successfully",
        data={"interviewer": InterviewerResponse.from_orm(interviewer)}
    )

# ---------------- Update Interviewer ----------------
@router.put("/{interviewer_id}", response_model=StandardResponse)
def update_interviewer(
    interviewer_id: int,
    payload: InterviewerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing interviewer completely.
    - Validates duplicates for emp_id, mobile, email against other records.
    - Updates availability time slots.
    """
    # Fetch existing interviewer
    interviewer = db.query(Interviewer).filter(
        Interviewer.id == interviewer_id,
        Interviewer.created_by == current_user.id
    ).first()

    if not interviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interviewer not found"
        )

    # Check for duplicate emp_id, mobile, or email with other records
    existing = db.query(Interviewer).filter(
        ((Interviewer.emp_id == payload.emp_id) |
         (Interviewer.mobile == payload.mobile) |
         (Interviewer.email == payload.email)) &
        (Interviewer.id != interviewer_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another interviewer with same emp_id, mobile, or email already exists"
        )

    # Update fields
    interviewer.emp_id = payload.emp_id
    interviewer.name = payload.name
    interviewer.skills = payload.skills
    interviewer.experience = payload.experience
    interviewer.mobile = payload.mobile
    interviewer.email = payload.email
    interviewer.availability = [slot.dict() for slot in payload.availability]
    interviewer.updated_at = datetime.utcnow()

    # Commit changes
    db.commit()
    db.refresh(interviewer)

    return StandardResponse(
        status="success",
        message="Interviewer updated successfully",
        data={"interviewer": InterviewerResponse.from_orm(interviewer)}
    )

# ---------------- Delete Interviewer ----------------
@router.delete("/{interviewer_id}", response_model=StandardResponse)
def delete_interviewer(
    interviewer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an interviewer permanently.
    Only the creator can delete.
    """
    interviewer = db.query(Interviewer).filter(
        Interviewer.id == interviewer_id,
        Interviewer.created_by == current_user.id
    ).first()

    if not interviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interviewer not found"
        )

    db.delete(interviewer)
    db.commit()

    return StandardResponse(
        status="success",
        message="Interviewer deleted successfully",
        data=None
    )
