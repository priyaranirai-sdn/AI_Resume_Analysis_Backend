from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey("requisitions.id"))
    candidate_name = Column(String, nullable=False)
    resume_filename = Column(String, nullable=False)
    resume_content = Column(Text, nullable=False)  # Extracted text from resume
    match_percentage = Column(Float, nullable=False)  # Overall match percentage
    confidence_score = Column(Float, nullable=False)  # AI confidence score
    is_match = Column(String, nullable=False)  # "Match", "Not a Match", "Partial Match"
    skills_match = Column(JSON)  # Skills found in resume vs required
    missing_skills = Column(JSON)  # Required skills not found in resume
    experience_match = Column(Boolean, default=False)  # Experience requirement met
    gaps_analysis = Column(Text)  # Detailed analysis of gaps
    suitability_rating = Column(String)  # "High", "Medium", "Low"
    analysis_details = Column(JSON)  # Detailed analysis results
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    requisition = relationship("Requisition", back_populates="resume_analyses")
    created_by_user = relationship("User", back_populates="resume_analyses")
