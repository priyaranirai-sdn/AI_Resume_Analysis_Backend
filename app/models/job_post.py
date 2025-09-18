from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime

class JobPost(Base):
    __tablename__ = "job_posts"
    
    # Primary key and unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key relationships
    requisition_id = Column(Integer, ForeignKey("requisitions.id"))  # Source requisition
    created_by = Column(Integer, ForeignKey("users.id"))  # Creating user
    
    # Core job information
    title = Column(String, nullable=False)  # Job title
    description = Column(Text, nullable=False)  # AI-generated comprehensive job description
    location = Column(String, nullable=False)
    experience_required = Column(Integer, nullable=False)
    
    # Job requirements and details
    skills_required = Column(JSON)  # List of required technical skills
    salary_range_min = Column(Integer)  # Minimum salary in the range
    salary_range_max = Column(Integer)  # Maximum salary in the range
    employment_type = Column(String, default="Full-time")  # Employment type
    
    # Job post lifecycle and status
    status = Column(String, default="Draft")  # Draft, Published, Closed
    published_portals = Column(JSON, default=lambda: [])  # List of portals where published
    external_job_ids = Column(JSON, default=lambda: {})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    requisition = relationship("Requisition", back_populates="job_posts")
    created_by_user = relationship("User", back_populates="job_posts")
