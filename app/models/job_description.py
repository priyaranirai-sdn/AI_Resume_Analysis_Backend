# from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from app.models.database import Base
# from datetime import datetime

# class JobDescription(Base):
#     __tablename__ = "job_descriptions"

#     id = Column(Integer, primary_key=True, index=True)
    
#     created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
#     description = Column(Text, nullable=False)
    
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationship with user who created this
#     created_by_user = relationship("User", back_populates="job_descriptions")


from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base
from app.models.associations import job_interviewers  # association table import

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    technology = Column(String(255), nullable=True)
    experience = Column(String(50), nullable=True)
    designation = Column(String(255), nullable=True)
    hr_screening = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_user = relationship("User", back_populates="job_descriptions")
    interviewers = relationship(
        "Interviewer",
        secondary=job_interviewers,
        back_populates="job_descriptions"
    )
