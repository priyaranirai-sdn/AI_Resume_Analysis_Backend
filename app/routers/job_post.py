from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.models.database import get_db
from app.models.job_post import JobPost
from app.models.requisition import Requisition
from app.models.user import User
from app.auth import get_current_user
from app.services.jd_generator_ultimate import generate_jd_ultimate
from datetime import datetime, timedelta
import logging

# Configure logging for job post operations
logger = logging.getLogger(__name__)

# Create router instance with job post prefix and tag
router = APIRouter(prefix="/job-post", tags=["Job Post"])

class JobPostCreate(BaseModel):
    """
    This model defines the minimal data required to create a job post from a requisition.
    The AI system will generate the complete job description automatically.
    """
    requisition_id: int  # ID of the requisition to create job post from
    expires_in_days: int = 30  # Default 30-day expiration for job posts

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
    description: str  # AI-generated job description
    location: str
    experience_required: int
    skills_required: List[str]
    salary_range_min: Optional[int]
    salary_range_max: Optional[int]
    employment_type: str
    status: str  # Draft, Published, Closed
    published_portals: List[str]  # List of portals where job is published
    external_job_ids: dict
    created_by: int
    created_at: datetime
    published_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class PortalPublishRequest(BaseModel):
    """
    job post publishing requests.
    """
    portals: List[str]

@router.post("/", response_model=JobPostResponse)
def create_job_post(
    job_post: JobPostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a job post from a requisition with AI-generated description.
    """
    import time
    
    try:
        # Validate requisition ownership and existence
        # This ensures users can only create job posts from their own requisitions
        requisition = db.query(Requisition).filter(
            Requisition.id == job_post.requisition_id,
            Requisition.created_by == current_user.id
        ).first()
        
        if not requisition:
            raise HTTPException(
                status_code=404,
                detail=f"Requisition with ID {job_post.requisition_id} not found or you don't have permission to access it"
            )
        
        # Log AI generation start for performance monitoring
        logger.info(f"Starting AI generation for requisition {requisition.id}...")
        start_time = time.time()
        
        # Generate job description using advanced AI technology
        try:
            ai_description = generate_jd_ultimate(
                designation=requisition.title,
                experience=requisition.experience_required,
                location=requisition.location,
                skills=requisition.skills_required,
                department=requisition.department
            )
        except Exception as ai_error:
            logger.error(f"AI generation failed: {ai_error}")
            from app.services.jd_generator_ultimate import create_ultimate_fallback_jd
            ai_description = create_ultimate_fallback_jd(
                designation=requisition.title,
                experience=requisition.experience_required,
                location=requisition.location,
                skills=requisition.skills_required,
                department=requisition.department
            )
            logger.info("Using fallback job description")
        
        generation_time = time.time() - start_time
        logger.info(f"Job description generated in {generation_time:.2f} seconds")
        
        expires_at = datetime.utcnow() + timedelta(days=job_post.expires_in_days)
        
        # Create job post with AI-generated content and requisition data
        db_job_post = JobPost(
            requisition_id=requisition.id,
            title=requisition.title,
            description=ai_description,  # AI-generated comprehensive description
            location=requisition.location,
            experience_required=requisition.experience_required,
            skills_required=requisition.skills_required,
            salary_range_min=requisition.salary_range_min,
            salary_range_max=requisition.salary_range_max,
            employment_type=requisition.employment_type,
            created_by=current_user.id,
            expires_at=expires_at
        )
        
        # Persist job post to database with transaction management
        # This ensures data consistency and proper error handling
        db.add(db_job_post)
        db.commit()
        db.refresh(db_job_post)
        
        logger.info(f"Job post created successfully with ID: {db_job_post.id}")
        return db_job_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_job_post: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create job post: {str(e)}"
        )

@router.get("/", response_model=List[JobPostResponse])
def get_job_posts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all job posts for the authenticated user.
    """
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
    """
    Retrieve a specific job post by ID.
    """
    # Query specific job post with user ownership validation
    # This ensures users can only access their own job posts
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
    """
    Update an existing job post with partial data.
    """
    # Validate job post ownership before allowing updates
    # This ensures users can only modify their own job posts
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    # Apply the updated data to the job post object
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
    # This ensures users can only publish their own job posts
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    # Simulate publishing
    published_portals = []
    external_job_ids = {}
    
    for portal in publish_request.portals:
        if portal.lower() in ["linkedin", "naukri", "indeed"]:
            external_id = f"{portal.upper()}_{job_post_id}_{datetime.now().strftime('%Y%m%d')}"
            external_job_ids[portal] = external_id
            published_portals.append(portal)
    
    # Update job post
    job_post.published_portals = published_portals
    job_post.external_job_ids = external_job_ids
    job_post.status = "Published"
    job_post.published_at = datetime.utcnow()
    
    # Persist publishing information to database
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
    """
    Regenerate job description using AI technology.
    """
    # Validate job post ownership before allowing regeneration
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    # Retrieve associated requisition for AI generation context
    requisition = db.query(Requisition).filter(
        Requisition.id == job_post.requisition_id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Associated requisition not found"
        )
    
    # Generate new job description using AI technology
    new_description = generate_jd(
        designation=requisition.title,
        experience=requisition.experience_required,
        location=requisition.location,
        skills=requisition.skills_required,
        department=requisition.department
    )
    
    # Update job post with new AI-generated description
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
    """
    Delete a job post permanently.
    """
    # Validate job post ownership before allowing deletion
    # This ensures users can only delete their own job posts
    job_post = db.query(JobPost).filter(
        JobPost.id == job_post_id,
        JobPost.created_by == current_user.id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="Job post not found"
        )
    
    # Permanently delete the job post from database
    # This operation cannot be undone, ensuring data integrity
    db.delete(job_post)
    db.commit()
    
    return {"message": "Job post deleted successfully"}

@router.get("/health/ai")
def check_ai_health():
    """
    Check AI model health and performance status.
    """
    try:
        from app.services.jd_generator_ultimate import get_model_info
        import time
        
        start_time = time.time()
        
        # Test fallback generation mechanism for reliability
        # This ensures the system remains functional even without AI models
        from app.services.jd_generator_ultimate import create_ultimate_fallback_jd
        test_start = time.time()
        
        try:
            # Test the fallback generation with sample data
            # This validates that the system can generate job descriptions
            test_jd = create_ultimate_fallback_jd(
                designation="Software Engineer",
                experience=3,
                location="Test City",
                skills=["Python", "FastAPI"],
                department="Technology"
            )
            test_time = time.time() - test_start
            load_time = time.time() - start_time
            
            # Get model information for detailed health reporting
            model_info = get_model_info()
            
            return {
                "status": "healthy",
                "message": "Job description generation is working (using fallback mode)",
                "load_time": load_time,
                "test_generation_time": test_time,
                "model_available": False,
                "fallback_mode": True,
                "model_name": model_info.get("model_name"),
                "model_type": model_info.get("model_type"),
                "test_jd_length": len(test_jd)
            }
            
        except Exception as e:
            # Handle fallback generation failures
            return {
                "status": "unhealthy",
                "message": f"Fallback generation test failed: {str(e)}",
                "load_time": load_time,
                "model_available": False
            }
        
    except Exception as e:
        # Handle overall health check failures
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check error: {str(e)}",
            "model_available": False
        }
