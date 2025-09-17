from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime

class JobPost(Base):
    __tablename__ = "job_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey("requisitions.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # AI-generated job description
    location = Column(String, nullable=False)
    experience_required = Column(Integer, nullable=False)
    skills_required = Column(JSON)
    salary_range_min = Column(Integer)
    salary_range_max = Column(Integer)
    employment_type = Column(String, default="Full-time")
    status = Column(String, default="Draft")  # Draft, Published, Closed
    published_portals = Column(JSON, default=lambda: [])  # List of portals where it's published
    external_job_ids = Column(JSON, default=lambda: {})  # External job IDs from different portals
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    requisition = relationship("Requisition", back_populates="job_posts")
    created_by_user = relationship("User", back_populates="job_posts")
