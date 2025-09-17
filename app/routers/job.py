from fastapi import APIRouter
from pydantic import BaseModel
from app.services.jd_generator_lazy import generate_jd

router = APIRouter(prefix="/job", tags=["Job Description"])

class JobRequest(BaseModel):
    designation: str
    experience: int
    location: str

@router.post("/generate")
def create_job_description(request: JobRequest):
    jd_text = generate_jd(
        designation=request.designation,
        experience=request.experience,
        location=request.location
    )
    return {"job_description": jd_text}
