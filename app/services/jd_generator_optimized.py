from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import re
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for lazy loading
_generator = None
_tokenizer = None
_model = None

def get_model_components():
    """Get model components with lazy loading and better error handling"""
    global _generator, _tokenizer, _model
    
    if _generator is None:
        try:
            logger.info("Loading optimized AI model for job description generation...")
            
            # Use a more appropriate model for text generation
            # GPT-2 is better suited for structured text generation than DialoGPT
            model_name = "gpt2"
            
            # Check if CUDA is available for faster inference
            device = 0 if torch.cuda.is_available() else -1
            logger.info(f"Using device: {'CUDA' if device == 0 else 'CPU'}")
            
            # Load tokenizer and model separately for better control
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == 0 else torch.float32,
                device_map="auto" if device == 0 else None
            )
            
            # Set pad token
            if _tokenizer.pad_token is None:
                _tokenizer.pad_token = _tokenizer.eos_token
            
            # Create pipeline with optimized settings
            _generator = pipeline(
                "text-generation",
                model=_model,
                tokenizer=_tokenizer,
                device=device,
                torch_dtype=torch.float16 if device == 0 else torch.float32
            )
            
            logger.info("AI model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            # Fallback to a simpler approach
            _generator = None
    
    return _generator

def generate_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Generates a comprehensive job description using optimized AI.
    """
    try:
        generator = get_model_components()
        
        if generator is None:
            logger.warning("AI model not available, using fallback")
            return create_fallback_jd(designation, experience, location, skills, department)
        
        skills_text = ", ".join(skills) if skills else "relevant technical skills"
        
        # Create a more structured prompt for better results
        prompt = f"""Job Title: {designation}
Department: {department or "Technology"}
Location: {location}
Experience: {experience}+ years
Skills: {skills_text}

Job Description:
We are looking for a {designation} to join our team. The ideal candidate will have {experience}+ years of experience in {skills_text}.

Key Responsibilities:
- Develop and maintain software applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Troubleshoot and debug applications

Required Qualifications:
- {experience}+ years of professional experience
- Strong proficiency in {skills_text}
- Bachelor's degree in Computer Science or related field
- Experience with version control systems
- Strong problem-solving skills

What We Offer:
- Competitive salary and benefits
- Flexible working arrangements
- Professional development opportunities
- Collaborative work environment

"""
        
        # Generate with optimized parameters
        response = generator(
            prompt,
            max_new_tokens=300,  # Increased for more comprehensive descriptions
            num_return_sequences=1,
            do_sample=True,
            temperature=0.8,  # Slightly higher for more creativity
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=generator.tokenizer.eos_token_id,
            truncation=True,
            return_full_text=False  # Only return generated text, not the prompt
        )
        
        generated_text = response[0]["generated_text"]
        
        # Clean up the generated text
        generated_text = generated_text.strip()
        
        # Remove any incomplete sentences at the end
        sentences = generated_text.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            generated_text = '.'.join(sentences[:-1]) + '.'
        
        # If the response is too short, use fallback
        if len(generated_text) < 150:
            logger.warning("Generated text too short, using fallback")
            return create_fallback_jd(designation, experience, location, skills, department)
            
        return generated_text
        
    except Exception as e:
        logger.error(f"Error generating JD with AI: {e}")
        return create_fallback_jd(designation, experience, location, skills, department)

def create_fallback_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Creates a comprehensive fallback job description when AI generation fails.
    """
    skills_text = ", ".join(skills) if skills else "relevant technical skills"
    
    return f"""# {designation}

**Department:** {department or "Technology"}  
**Location:** {location}  
**Experience Required:** {experience}+ years

## Job Summary
We are seeking a talented and experienced {designation} to join our dynamic team. The ideal candidate will have {experience}+ years of experience in {skills_text} and be passionate about delivering high-quality solutions.

## Key Responsibilities
- Design, develop, and maintain software applications
- Collaborate with cross-functional teams to define, design, and ship new features
- Write clean, maintainable, and efficient code
- Participate in code reviews and technical discussions
- Troubleshoot and debug applications
- Stay up-to-date with emerging technologies and industry trends
- Mentor junior developers and contribute to team knowledge sharing

## Required Qualifications
- {experience}+ years of professional experience in software development
- Strong proficiency in {skills_text}
- Bachelor's degree in Computer Science or related field
- Experience with version control systems (Git)
- Strong problem-solving and analytical skills
- Excellent communication and teamwork abilities
- Experience with agile development methodologies

## Preferred Skills
- Experience with cloud platforms (AWS, Azure, or GCP)
- Knowledge of containerization technologies (Docker, Kubernetes)
- Experience with testing frameworks and CI/CD pipelines
- Familiarity with DevOps practices
- Experience with microservices architecture
- Knowledge of database design and optimization

## What We Offer
- Competitive salary and comprehensive benefits package
- Flexible working arrangements and remote work options
- Professional development opportunities and training budget
- Collaborative and innovative work environment
- Health and wellness programs
- Generous vacation and time-off policies
- Career advancement opportunities

## Application Process
If you are passionate about technology and meet the above requirements, we would love to hear from you. Please submit your resume and cover letter detailing your relevant experience.

Join our team and be part of building the future of technology!
"""

def clear_model_cache():
    """Clear the model cache to free up memory"""
    global _generator, _tokenizer, _model
    _generator = None
    _tokenizer = None
    _model = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("Model cache cleared")
