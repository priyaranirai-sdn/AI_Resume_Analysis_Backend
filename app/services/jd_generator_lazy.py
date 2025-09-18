from transformers import pipeline
import re

# Global variable to store the generator
_generator = None

def get_generator():
    """Get the generator instance """
    global _generator
    if _generator is None:
        print("Loading AI model... This may take a moment.")
        _generator = pipeline("text-generation", model="microsoft/DialoGPT-medium")
    return _generator

def generate_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Generate a comprehensive job description using AI technology
    """
    # This ensures proper formatting in the AI prompt
    skills_text = ", ".join(skills) if skills else "relevant technical skills"

    # This prompt engineering approach improves generation quality
    prompt = f"""Job Title: {designation}
Department: {department or "Technology"}
Location: {location}
Experience Required: {experience}+ years
Key Skills: {skills_text}

Write a professional job description with the following sections:
1. Job Summary
2. Key Responsibilities
3. Required Qualifications
4. Preferred Skills
5. What We Offer

Format it like a LinkedIn job posting:"""

    try:
        generator = get_generator()
        
        # Generate job description using AI model
        response = generator(
            prompt, 
            max_new_tokens=256,  # Limit output length for performance
            num_return_sequences=1,  # Generate single response
            do_sample=True,  # Enable sampling for creativity
            temperature=0.7,  # Balance creativity and coherence
            pad_token_id=generator.tokenizer.eos_token_id,  # Handle padding
            truncation=True  # Enable truncation for long inputs
        )
        
        generated_text = response[0]["generated_text"]
        
        # Clean up the generated text
        if "Write a professional job description" in generated_text:
            generated_text = generated_text.split("Write a professional job description")[1]

        generated_text = generated_text.strip()
        
        if len(generated_text) < 200:
            return create_fallback_jd(designation, experience, location, skills, department)
            
        return generated_text
        
    except Exception as e:
        print(f"Error generating JD with AI: {e}")
        return create_fallback_jd(designation, experience, location, skills, department)

def create_fallback_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    skills_text = ", ".join(skills) if skills else "relevant technical skills"
    return f"""
# {designation}

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

## Required Qualifications
- {experience}+ years of professional experience in software development
- Strong proficiency in {skills_text}
- Bachelor's degree in Computer Science or related field
- Experience with version control systems (Git)
- Strong problem-solving and analytical skills
- Excellent communication and teamwork abilities

## Preferred Skills
- Experience with cloud platforms (AWS, Azure, or GCP)
- Knowledge of agile development methodologies
- Experience with testing frameworks
- Familiarity with DevOps practices

## What We Offer
- Competitive salary and benefits package
- Flexible working arrangements
- Professional development opportunities
- Collaborative and innovative work environment
- Health and wellness programs

Join our team and be part of building the future of technology!
"""
