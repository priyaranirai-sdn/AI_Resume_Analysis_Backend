from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime

class Requisition(Base):
    __tablename__ = "requisitions"
    
    # Primary key and unique identifier
    id = Column(Integer, primary_key=True, index=True)
    # Core job information
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    location = Column(String, nullable=False)
    experience_required = Column(Integer, nullable=False)
    
    # Job requirements and details
    skills_required = Column(JSON)  # List of required technical skills
    responsibilities = Column(Text)  # Detailed job responsibilities
    qualifications = Column(Text)  # Required qualifications and education
    salary_range_min = Column(Integer)  # Minimum salary in the range
    salary_range_max = Column(Integer)  # Maximum salary in the range
    employment_type = Column(String, default="Full-time")  # Full-time, Part-time, Contract
    
    # Requisition lifecycle and status
    status = Column(String, default="Draft")  # Draft, Approved, Rejected
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User", back_populates="requisitions")
    job_posts = relationship("JobPost", back_populates="requisition")
    resume_analyses = relationship("ResumeAnalysis", back_populates="requisition")
