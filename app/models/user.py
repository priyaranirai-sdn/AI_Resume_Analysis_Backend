from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """User model representing HR managers"""
    __tablename__ = "users"
    
    # Primary key and unique identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication credentials
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User profile information
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    api_key = Column(String, unique=True, default=lambda: secrets.token_urlsafe(32))
    
    # Relationships
    requisitions = relationship("Requisition", back_populates="created_by_user")
    job_posts = relationship("JobPost", back_populates="created_by_user")
    resume_analyses = relationship("ResumeAnalysis", back_populates="created_by_user")
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
