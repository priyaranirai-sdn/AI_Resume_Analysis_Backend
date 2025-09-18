from .database import Base, engine, get_db
from .user import User
from .requisition import Requisition
from .job_post import JobPost
from .resume_analysis import ResumeAnalysis

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
