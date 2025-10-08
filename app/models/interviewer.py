# # from sqlalchemy import JSON, Column, Integer, String, Text, DateTime, ForeignKey
# # from sqlalchemy.orm import relationship
# # from app.models.database import Base
# # from datetime import datetime

# # class Interviewer(Base):
# #     __tablename__ = "interviewers"

# #     id = Column(Integer, primary_key=True, index=True)
# #     name = Column(String(255), nullable=False)
# #     skills = Column(JSON) 
# #     experience = Column(Integer, default=0)
# #     mobile = Column(String(20), nullable=False, unique=True)
# #     email = Column(String(255), nullable=False, unique=True)
# #     created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
# #     created_at = Column(DateTime, default=datetime.utcnow)
# #     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
# #     created_by_user = relationship("User", back_populates="interviewers")

# from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.models.database import Base
# from app.models.associations import job_interviewers  # association table import

# class Interviewer(Base):
#     __tablename__ = "interviewers"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     # emp_id = Column(String(50), nullable=False)
#     skills = Column(JSON, nullable=True)
#     experience = Column(Integer, default=0)
#     mobile = Column(String(20), nullable=False, unique=True)
#     email = Column(String(255), nullable=False, unique=True)
#     created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     created_by_user = relationship("User", back_populates="interviewers")
#     job_descriptions = relationship(
#         "JobDescription",
#         secondary=job_interviewers,
#         back_populates="interviewers"
#     )

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base
from app.models.associations import job_interviewers  # association table import


class Interviewer(Base):
    __tablename__ = "interviewers"

    id = Column(Integer, primary_key=True, index=True)
    
    # ✅ Employee ID
    emp_id = Column(String(50), nullable=False, unique=True)  # unique company-level interviewer ID
    
    name = Column(String(255), nullable=False)
    skills = Column(JSON, nullable=True)
    experience = Column(Integer, default=0)
    mobile = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)

    # ✅ Availability (Time slots)
    # Format: [{"start": "09:00", "end": "11:00"}, {"start": "14:00", "end": "16:00"}]
    availability = Column(JSON, nullable=True, default=[])

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by_user = relationship("User", back_populates="interviewers")
    job_descriptions = relationship(
        "JobDescription",
        secondary=job_interviewers,
        back_populates="interviewers"
    )
