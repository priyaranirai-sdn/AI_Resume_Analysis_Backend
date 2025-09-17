from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.models.database import get_db
from app.models.resume_analysis import ResumeAnalysis
from app.models.requisition import Requisition
from app.models.job_post import JobPost
from app.models.user import User
from app.auth import get_current_user
from app.services.resume_analyzer import resume_analyzer
from datetime import datetime

router = APIRouter(prefix="/resume-analysis", tags=["Resume Analysis"])

class ResumeAnalysisRequest(BaseModel):
    requisition_id: int
    candidate_name: str

class ResumeAnalysisResponse(BaseModel):
    id: int
    requisition_id: int
    candidate_name: str
    resume_filename: str
    match_percentage: float
    confidence_score: float
    is_match: str
    skills_match: dict
    missing_skills: List[str]
    experience_match: bool
    gaps_analysis: str
    suitability_rating: str
    analysis_details: dict
    created_at: datetime

    class Config:
        from_attributes = True

class BulkAnalysisResponse(BaseModel):
    total_candidates: int
    matches: int
    partial_matches: int
    not_matches: int
    candidates: List[ResumeAnalysisResponse]

@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    requisition_id: int = Form(...),
    candidate_name: str = Form(...),
    resume_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a single resume against a job requisition"""
    
    # Validate file type
    if not resume_file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, DOCX, and TXT files are supported"
        )
    
    # Get requisition and job post
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    # Get job post for the requisition
    job_post = db.query(JobPost).filter(
        JobPost.requisition_id == requisition_id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="No job post found for this requisition"
        )
    
    try:
        # Read file content
        file_content = await resume_file.read()
        
        # Extract text from resume
        resume_text = resume_analyzer.extract_text_from_file(file_content, resume_file.filename)
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the resume file"
            )
        
        # Analyze resume match
        analysis_result = resume_analyzer.analyze_resume_match(
            resume_text=resume_text,
            job_description=job_post.description,
            required_skills=requisition.skills_required or [],
            required_experience=requisition.experience_required
        )
        
        # Save analysis to database
        db_analysis = ResumeAnalysis(
            requisition_id=requisition_id,
            candidate_name=candidate_name,
            resume_filename=resume_file.filename,
            resume_content=resume_text,
            match_percentage=analysis_result["match_percentage"],
            confidence_score=analysis_result["confidence_score"],
            is_match=analysis_result["is_match"],
            skills_match=analysis_result["skills_match"],
            missing_skills=analysis_result["skills_match"]["missing_skills"],
            experience_match=analysis_result["experience_match"],
            gaps_analysis=analysis_result["gaps_analysis"],
            suitability_rating=analysis_result["suitability_rating"],
            analysis_details=analysis_result,
            created_by=current_user.id
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return db_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )

@router.post("/analyze-bulk", response_model=BulkAnalysisResponse)
async def analyze_multiple_resumes(
    requisition_id: int = Form(...),
    resume_files: List[UploadFile] = File(...),
    candidate_names: str = Form(...),  # JSON string of candidate names
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze multiple resumes against a job requisition"""
    
    import json
    
    try:
        # Try to parse as JSON first
        candidate_names_list = json.loads(candidate_names)
    except json.JSONDecodeError:
        # If JSON parsing fails, try comma-separated string
        try:
            candidate_names_list = [name.strip() for name in candidate_names.split(',')]
            print(f"Parsed candidate names as comma-separated: {candidate_names_list}")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"candidate_names must be a valid JSON array or comma-separated string. Error: {str(e)}"
            )
    
    if len(resume_files) != len(candidate_names_list):
        raise HTTPException(
            status_code=400,
            detail="Number of files must match number of candidate names"
        )
    
    # Get requisition and job post
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    job_post = db.query(JobPost).filter(
        JobPost.requisition_id == requisition_id
    ).first()
    
    if not job_post:
        raise HTTPException(
            status_code=404,
            detail="No job post found for this requisition"
        )
    
    analyses = []
    matches = 0
    partial_matches = 0
    not_matches = 0
    
    for i, (resume_file, candidate_name) in enumerate(zip(resume_files, candidate_names_list)):
        try:
            # Validate file type
            if not resume_file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                continue
            
            # Read file content
            file_content = await resume_file.read()
            
            # Extract text from resume
            resume_text = resume_analyzer.extract_text_from_file(file_content, resume_file.filename)
            
            if not resume_text.strip():
                continue
            
            # Analyze resume match
            analysis_result = resume_analyzer.analyze_resume_match(
                resume_text=resume_text,
                job_description=job_post.description,
                required_skills=requisition.skills_required or [],
                required_experience=requisition.experience_required
            )
            
            # Save analysis to database
            db_analysis = ResumeAnalysis(
                requisition_id=requisition_id,
                candidate_name=candidate_name,
                resume_filename=resume_file.filename,
                resume_content=resume_text,
                match_percentage=analysis_result["match_percentage"],
                confidence_score=analysis_result["confidence_score"],
                is_match=analysis_result["is_match"],
                skills_match=analysis_result["skills_match"],
                missing_skills=analysis_result["skills_match"]["missing_skills"],
                experience_match=analysis_result["experience_match"],
                gaps_analysis=analysis_result["gaps_analysis"],
                suitability_rating=analysis_result["suitability_rating"],
                analysis_details=analysis_result,
                created_by=current_user.id
            )
            
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            
            analyses.append(db_analysis)
            
            # Count matches
            if analysis_result["is_match"] == "Match":
                matches += 1
            elif analysis_result["is_match"] == "Partial Match":
                partial_matches += 1
            else:
                not_matches += 1
                
        except Exception as e:
            print(f"Error processing {resume_file.filename}: {str(e)}")
            continue
    
    return BulkAnalysisResponse(
        total_candidates=len(analyses),
        matches=matches,
        partial_matches=partial_matches,
        not_matches=not_matches,
        candidates=analyses
    )

@router.get("/requisition/{requisition_id}", response_model=List[ResumeAnalysisResponse])
def get_resume_analyses(
    requisition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all resume analyses for a specific requisition"""
    
    # Verify requisition belongs to user
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    analyses = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.requisition_id == requisition_id
    ).order_by(ResumeAnalysis.match_percentage.desc()).all()
    
    return analyses

@router.get("/analysis/{analysis_id}", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume analysis by ID"""
    
    analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.id == analysis_id,
        ResumeAnalysis.created_by == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found"
        )
    
    return analysis

@router.get("/summary/{requisition_id}")
def get_analysis_summary(
    requisition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis summary for a requisition"""
    
    # Verify requisition belongs to user
    requisition = db.query(Requisition).filter(
        Requisition.id == requisition_id,
        Requisition.created_by == current_user.id
    ).first()
    
    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )
    
    analyses = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.requisition_id == requisition_id
    ).all()
    
    if not analyses:
        return {
            "total_candidates": 0,
            "matches": 0,
            "partial_matches": 0,
            "not_matches": 0,
            "average_match_percentage": 0,
            "top_candidates": []
        }
    
    matches = sum(1 for a in analyses if a.is_match == "Match")
    partial_matches = sum(1 for a in analyses if a.is_match == "Partial Match")
    not_matches = sum(1 for a in analyses if a.is_match == "Not a Match")
    average_match = sum(a.match_percentage for a in analyses) / len(analyses)
    
    # Get top 5 candidates
    top_candidates = sorted(analyses, key=lambda x: x.match_percentage, reverse=True)[:5]
    
    return {
        "total_candidates": len(analyses),
        "matches": matches,
        "partial_matches": partial_matches,
        "not_matches": not_matches,
        "average_match_percentage": round(average_match, 2),
        "top_candidates": [
            {
                "candidate_name": c.candidate_name,
                "match_percentage": c.match_percentage,
                "is_match": c.is_match,
                "suitability_rating": c.suitability_rating
            }
            for c in top_candidates
        ]
    }

@router.delete("/analysis/{analysis_id}")
def delete_resume_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume analysis"""
    
    analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.id == analysis_id,
        ResumeAnalysis.created_by == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found"
        )
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Resume analysis deleted successfully"}
