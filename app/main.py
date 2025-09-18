from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.routers import job, auth, requisition, job_post, resume_analysis
from app.models import create_tables
from app.utils.error_handlers import (
    validation_exception_handler,
    integrity_error_handler,
    general_exception_handler
)

# Create database tables
create_tables()

app = FastAPI(
    title="TalentFitAI Backend",
    description="AI-powered Job Description Generator and HR Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include all routers
app.include_router(auth.router)
app.include_router(requisition.router)
app.include_router(job_post.router)
app.include_router(job.router)  # Keep the original job router for backward compatibility
app.include_router(resume_analysis.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to TalentFitAI Backend 🚀",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "HR Manager Authentication",
            "Job Requisition Management", 
            "AI-powered Job Description Generation",
            "Job Post Publishing to External Portals"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "TalentFitAI is running"}
