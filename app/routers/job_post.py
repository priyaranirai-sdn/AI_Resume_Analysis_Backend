from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.models.database import get_db
from app.models.job_post import JobPost
from app.models.requisition import Requisition
from app.models.user import User
from app.auth import get_current_user
from app.services.jd_generator import generate_jd
from datetime import datetime, timedelta

router = APIRouter(prefix="/job-post", tags=["Job Post"])

class JobPostCreate(BaseModel):
    requisition_id: int
    expires_in_days: int = 30

class JobPostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[int] = None
    skills_required: Optional[List[str]] = None
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None

class JobPostResponse(BaseModel):
    id: int
    requisition_id: int
    title: str
    description: str
    location: str
    experience_required: int
    skills_required: List[str]
    salary_range_min: Optional[int]
    salary_range_max: Optional[int]
    employment_type: str
    status: str
    published_portals: List[str]
    external_job_ids: dict
    created_by: int
    created_at: datetime
    published_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class PortalPublishRequest(BaseModel):
    portals: List[str]  # ["linkedin", "naukri", "indeed"]

@router.post("/", response_model=JobPostResponse)
def create_job_post(
    job_post: JobPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a job post from a requisition with AI-generated description"""
    # Get the requisition
    requisition = db.query(Requisition).filter(
        Requisition.id == job_post.requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    # Generate job description using AI
    ai_description = generate_jd(
        designation=requisition.title,
        experience=requisition.experience_required,
        location=requisition.location,
        skills=requisition.skills_required,
        department=requisition.department
    )
    
    # Calculate expiry date
    expires_at = datetime.utcnow() + timedelta(days=job_post.expires_in_days)
    
    # Create job post
    db_job_post = JobPost(
        requisition_id=requisition.id,
        title=requisition.title,
        description=ai_description,
        location=requisition.location,
        experience_required=requisition.experience_required,
        skills_required=requisition.skills_required,
        salary_range_min=requisition.salary_range_min,
        salary_range_max=requisition.salary_range_max,
        employment_type=requisition.employment_type,
        created_by=current_user.id,
        expires_at=expires_at
    )
    
    db.add(db_job_post)
    db.commit()
    db.refresh(db_job_post)
    
    return db_job_post

@router.get("/", response_model=List[JobPostResponse])
def get_job_posts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all job posts for the current user"""
    job_posts = db.query(JobPost).filter(
        JobPost.created_by == current_user.id
    ).offset(skip).limit(limit).all()
    return job_posts

@router.get("/{job_post_id}", response_model=JobPostResponse)
def get_job_post(
    job_post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific job post by ID"""
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    return job_post

@router.put("/{job_post_id}", response_model=JobPostResponse)
def update_job_post(
    job_post_id: int,
    job_post_update: JobPostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a job post"""
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    # Update only provided fields
    update_data = job_post_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_post, field, value)
    
    db.commit()
    db.refresh(job_post)
    
    return job_post

@router.post("/{job_post_id}/publish")
def publish_job_post(
    job_post_id: int,
    publish_request: PortalPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish job post to external portals (simulated)"""
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    # Simulate publishing to external portals
    published_portals = []
    external_job_ids = {}
    
    for portal in publish_request.portals:
        if portal.lower() in ["linkedin", "naukri", "indeed"]:
            # Simulate external job ID generation
            external_id = f"{portal.upper()}_{job_post_id}_{datetime.now().strftime('%Y%m%d')}"
            external_job_ids[portal] = external_id
            published_portals.append(portal)
    
    # Update job post with publishing information
    job_post.published_portals = published_portals
    job_post.external_job_ids = external_job_ids
    job_post.status = "Published"
    job_post.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job_post)
    
    return {
        "message": f"Job post published to {len(published_portals)} portals",
        "published_portals": published_portals,
        "external_job_ids": external_job_ids
    }

@router.post("/{job_post_id}/regenerate-description")
def regenerate_job_description(
    job_post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate job description using AI"""
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    # Get requisition details
    requisition = db.query(Requisition).filter(
        Requisition.id == job_post.requisition_id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Associated requisition not found"
        )
    
    # Generate new job description using AI
    new_description = generate_jd(
        designation=requisition.title,
        experience=requisition.experience_required,
        location=requisition.location,
        skills=requisition.skills_required,
        department=requisition.department
    )
    
    # Update job post with new description
    job_post.description = new_description
    db.commit()
    db.refresh(job_post)
    
    return {
        "message": "Job description regenerated successfully",
        "new_description": new_description
    }

@router.delete("/{job_post_id}")
def delete_job_post(
    job_post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job post"""
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    db.delete(job_post)
    db.commit()
    
    return {"message": "Job post deleted successfully"}
