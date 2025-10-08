from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.database import Base

job_interviewers = Table(
    "job_interviewers",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("job_descriptions.id"), primary_key=True),
    Column("interviewer_id", Integer, ForeignKey("interviewers.id"), primary_key=True)
)
