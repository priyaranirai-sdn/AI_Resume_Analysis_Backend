from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.database import get_db
from app.models.job_description import JobDescription
from app.models.interviewer import Interviewer
from app.models.user import User
from app.auth import get_current_user  # Authentication dependency

router = APIRouter(prefix="/job-description", tags=["Job Description"])

# ---------------- Schemas ----------------
class InterviewerResponse(BaseModel):
    id: int
    name: str
    skills: Optional[List[str]] = []
    experience: int
    mobile: str
    email: str

    model_config = {"from_attributes": True}


class JobDescriptionCreate(BaseModel):
    title: str
    description: str
    technology: Optional[str] = None
    experience: Optional[str] = None
    designation: Optional[str] = None
    hr_screening: Optional[dict] = None
    interviewers: Optional[List[int]] = []  # Assign interviewers while creating/updating


class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    description: str
    technology: Optional[str] = None
    experience: Optional[str] = None
    designation: Optional[str] = None
    hr_screening: Optional[dict] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    interviewers: List[InterviewerResponse] = []

    model_config = {"from_attributes": True}


class StandardResponse(BaseModel):
    status: str  # 'success' or 'error'
    message: str
    data: dict | list | None = None


# ---------------- Routes ----------------
@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jd = JobDescription(
        title=payload.title,
        description=payload.description,
        technology=payload.technology,
        experience=payload.experience,
        designation=payload.designation,
        hr_screening=payload.hr_screening,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Assign interviewers if provided
    if payload.interviewers:
        interviewers = db.query(Interviewer).filter(Interviewer.id.in_(payload.interviewers)).all()
        jd.interviewers = interviewers

    db.add(jd)
    db.commit()
    db.refresh(jd)

    jd_response = JobDescriptionResponse.from_orm(jd)
    return StandardResponse(
        status="success",
        message="Job Description created successfully",
        data={"job_description": jd_response}
    )


@router.get("/", response_model=StandardResponse)
def get_all_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jds = db.query(JobDescription).filter(JobDescription.created_by == current_user.id).all()
    jd_list = [JobDescriptionResponse.from_orm(jd) for jd in jds]

    return StandardResponse(
        status="success",
        message=f"{len(jd_list)} job description(s) retrieved successfully",
        data={"job_descriptions": jd_list}
    )


@router.get("/{jd_id}", response_model=StandardResponse)
def get_job_description(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id,
        JobDescription.created_by == current_user.id
    ).first()

    if not jd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Description not found")

    jd_response = JobDescriptionResponse.from_orm(jd)
    return StandardResponse(
        status="success",
        message="Job Description retrieved successfully",
        data={"job_description": jd_response}
    )


@router.put("/{jd_id}", response_model=StandardResponse)
def update_job_description(
    jd_id: int,
    payload: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id,
        JobDescription.created_by == current_user.id
    ).first()

    if not jd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Description not found")

    jd.title = payload.title
    jd.description = payload.description
    jd.technology = payload.technology
    jd.experience = payload.experience
    jd.designation = payload.designation
    jd.hr_screening = payload.hr_screening
    jd.updated_at = datetime.utcnow()

    # Update interviewers if provided
    if payload.interviewers is not None:
        print("hellooo",payload)
        interviewers = db.query(Interviewer).filter(Interviewer.id.in_(payload.interviewers)).all()
        jd.interviewers = interviewers

    db.commit()
    db.refresh(jd)

    jd_response = JobDescriptionResponse.from_orm(jd)
    return StandardResponse(
        status="success",
        message="Job Description updated successfully",
        data={"job_description": jd_response}
    )


@router.delete("/{jd_id}", response_model=StandardResponse)
def delete_job_description(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id,
        JobDescription.created_by == current_user.id
    ).first()

    if not jd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Description not found")

    db.delete(jd)
    db.commit()

    return StandardResponse(
        status="success",
        message="Job Description deleted successfully",
        data=None
    )
