# from fastapi import APIRouter
# from pydantic import BaseModel
# from app.services.jd_generator_lazy import generate_jd

# router = APIRouter(prefix="/job", tags=["Job Description"])

# class JobRequest(BaseModel):
#     designation: str
#     experience: int
#     location: str

# @router.post("/generate")
# def create_job_description(request: JobRequest):
#     jd_text = generate_jd(
#         designation=request.designation,
#         experience=request.experience,
#         location=request.location
#     )
#     return {"job_description": jd_text}

# app/routers/job_router.py
from requests import Session
from app.models.database import get_db
from fastapi import APIRouter,Depends
from pydantic import BaseModel
from app.services.jd_generator_lazy import generate_jd
from app.services.screening_question_generator import generate_screening_questions
from app.models.user import User
from app.auth import get_current_user 
router = APIRouter(prefix="/job", tags=["Job Description"])

# -------------------- Request Schemas --------------------
class JobRequest(BaseModel):
    designation: str
    experience: int
    location: str
    skills: list[str] = []  # optional
    department: str = None   # optional

class ScreeningRequest(BaseModel):
    job_description: str

# -------------------- Routes --------------------
@router.post("/generate")
def create_job_description(request: JobRequest):
    """
    Generate a full job description based on designation, experience, location, skills, and department.
    """
    jd_text = generate_jd(
        designation=request.designation,
        experience=request.experience,
        location=request.location,
        skills=request.skills,
        department=request.department
    )
    return {"job_description": jd_text}


# @router.post("/generate-screening")
# def create_screening_questions(request: ScreeningRequest,  current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)):
#     """
#     Generate a list of screening questions based on the provided job description text.
#     """
#     questions = generate_screening_questions(request.job_description)
#     return {"screening_questions": questions}

@router.post("/generate-screening")
async def create_screening_questions(
    request: ScreeningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    questions = await generate_screening_questions(request.job_description)  # async version
    # numbered_questions = {f"q{i+1}": q for i, q in enumerate(questions)}
    return {"screening_questions": questions}
