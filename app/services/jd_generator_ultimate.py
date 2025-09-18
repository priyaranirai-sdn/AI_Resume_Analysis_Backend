import re
import time
import threading
import random
from typing import Optional, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Global variable to store the generator (lazy loading)
_generator = None
_model_info = None

# AI model functionality removed for stability

def get_optimized_generator():
    """Get the optimized generator instance (lazy loading)"""
    global _generator
    if _generator is None:
        print("Loading fast AI model for job description generation...")
        try:
            # Use a small, fast model that's perfect for text generation
            model_name = "microsoft/DialoGPT-small"  # Much smaller and faster than medium
            
            # Load with optimized settings for speed
            _generator = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1,  # Use GPU if available, otherwise CPU
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,  # Use half precision on GPU
                model_kwargs={
                    "pad_token_id": 50256,  # Set pad token
                    "max_length": 512,
                }
            )
            print("✅ Fast AI model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading AI model: {e}")
            print("🔄 Falling back to template-based generation")
            _generator = None
    
    return _generator

def get_model_info() -> Dict[str, Any]:
    """Get information about the loaded model"""
    global _model_info
    if _model_info is None:
        generator = get_optimized_generator()
        if generator:
            try:
                _model_info = {
                    "model_name": "microsoft/DialoGPT-small",
                    "model_type": "text-generation",
                    "device": "cuda" if torch.cuda.is_available() else "cpu",
                    "max_length": 512,
                    "vocab_size": 50257,
                    "status": "ai_model_loaded",
                    "torch_dtype": "float16" if torch.cuda.is_available() else "float32"
                }
            except Exception as e:
                print(f"Error getting model info: {e}")
                _model_info = {
                    "model_name": "microsoft/DialoGPT-small",
                    "model_type": "text-generation",
                    "device": "cpu",
                    "max_length": 512,
                    "vocab_size": 50257,
                    "status": "ai_model_loaded"
                }
        else:
            _model_info = {
                "model_name": "template_fallback",
                "model_type": "template-based",
                "device": "cpu",
                "max_length": 512,
                "vocab_size": 0,
                "status": "using_fallback"
            }
    return _model_info

def generate_fast_ai_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Fast AI-like job description generation using templates and randomization.
    Returns varied, professional job descriptions quickly.
    """
    skills_text = ", ".join(skills) if skills else "relevant technical skills"
    department = department or "Technology"
    
    # Job summary templates
    summaries = [
        f"We are seeking a talented and experienced {designation} to join our innovative team in {location}. The ideal candidate will bring {experience}+ years of expertise in {skills_text} and demonstrate a passion for delivering exceptional results in a fast-paced, collaborative environment.",
        f"Join our dynamic team as a {designation} in {location}! We're looking for a skilled professional with {experience}+ years of experience in {skills_text} who thrives in an agile, technology-driven environment.",
        f"Our company is seeking a passionate {designation} to contribute to our growing team in {location}. The successful candidate will have {experience}+ years of experience with {skills_text} and a strong desire to work on cutting-edge projects.",
        f"We're hiring a {designation} to join our {department} team in {location}. We need someone with {experience}+ years of experience in {skills_text} who can drive innovation and deliver high-quality solutions."
    ]
    
    # Responsibility templates
    responsibilities = [
        [
            f"Design, develop, and maintain scalable software applications using {skills_text}",
            "Collaborate with cross-functional teams to define, design, and ship new features",
            "Write clean, maintainable, and well-documented code following best practices",
            "Participate in code reviews and technical discussions to ensure code quality",
            "Troubleshoot and debug applications to identify and resolve issues",
            "Stay current with emerging technologies and industry trends",
            "Mentor junior developers and contribute to team knowledge sharing",
            "Work closely with product managers and designers to deliver exceptional user experiences"
        ],
        [
            f"Lead the development of complex software solutions using {skills_text}",
            "Architect and implement robust, scalable systems and applications",
            "Collaborate with stakeholders to understand requirements and deliver solutions",
            "Optimize application performance and ensure high availability",
            "Implement automated testing and continuous integration processes",
            "Provide technical leadership and guidance to development teams",
            "Research and evaluate new technologies to improve our tech stack",
            "Document technical specifications and maintain system documentation"
        ],
        [
            f"Build and maintain high-performance applications with {skills_text}",
            "Work in an agile environment to deliver features on time and within scope",
            "Collaborate with QA teams to ensure comprehensive test coverage",
            "Contribute to architectural decisions and technical strategy",
            "Implement security best practices and data protection measures",
            "Optimize database queries and improve system performance",
            "Participate in sprint planning and retrospective meetings",
            "Provide production support and troubleshoot critical issues"
        ]
    ]
    
    # Qualification templates
    qualifications = [
        [
            f"{experience}+ years of professional experience in software development",
            f"Strong proficiency in {skills_text}",
            "Bachelor's degree in Computer Science, Engineering, or related field",
            "Experience with version control systems (Git) and collaborative development",
            "Strong problem-solving and analytical thinking skills",
            "Excellent communication and teamwork abilities",
            "Experience with agile development methodologies",
            "Knowledge of software testing principles and practices"
        ],
        [
            f"Minimum {experience} years of hands-on experience in software development",
            f"Expert-level knowledge of {skills_text}",
            "Degree in Computer Science, Software Engineering, or equivalent experience",
            "Proven track record of delivering high-quality software solutions",
            "Strong understanding of software architecture and design patterns",
            "Experience with modern development tools and practices",
            "Ability to work independently and as part of a team",
            "Excellent verbal and written communication skills"
        ]
    ]
    
    # Preferred skills templates
    preferred_skills = [
        [
            "Experience with cloud platforms (AWS, Azure, or Google Cloud)",
            "Knowledge of containerization technologies (Docker, Kubernetes)",
            "Experience with microservices architecture",
            "Familiarity with DevOps practices and CI/CD pipelines",
            "Experience with database design and optimization",
            "Knowledge of security best practices and compliance",
            "Experience with API design and development",
            "Familiarity with monitoring and logging tools"
        ],
        [
            "Experience with modern frontend frameworks (React, Angular, Vue.js)",
            "Knowledge of mobile development (iOS/Android or React Native)",
            "Experience with data science and machine learning tools",
            "Familiarity with blockchain or cryptocurrency technologies",
            "Experience with enterprise software development",
            "Knowledge of performance optimization techniques",
            "Experience with internationalization and localization",
            "Familiarity with accessibility standards and practices"
        ]
    ]
    
    # Benefits templates
    benefits = [
        [
            "Competitive salary and comprehensive benefits package",
            "Flexible working arrangements and remote work options",
            "Professional development opportunities and training budget",
            "Collaborative and innovative work environment",
            "Health and wellness programs",
            "Stock options and equity participation",
            "Generous paid time off and holiday schedule",
            "Modern office space with cutting-edge technology"
        ],
        [
            "Attractive compensation package with performance bonuses",
            "Work-life balance with flexible hours and remote options",
            "Continuous learning opportunities and conference attendance",
            "Dynamic, fast-paced startup environment",
            "Comprehensive health, dental, and vision insurance",
            "401(k) matching and retirement planning",
            "Team building events and company outings",
            "Opportunity to work with the latest technologies"
        ]
    ]
    
    # Randomly select templates
    summary = random.choice(summaries)
    responsibility_set = random.choice(responsibilities)
    qualification_set = random.choice(qualifications)
    preferred_set = random.choice(preferred_skills)
    benefit_set = random.choice(benefits)
    
    # Shuffle some lists for variety
    random.shuffle(responsibility_set)
    random.shuffle(preferred_set)
    
    # Generate the job description
    jd = f"""# {designation}

**Department:** {department}  
**Location:** {location}  
**Experience Required:** {experience}+ years  
**Employment Type:** Full-time

## Job Summary

{summary}

As a {designation}, you will play a crucial role in driving our technology initiatives forward while contributing to our company's growth and success. This position offers an excellent opportunity to work with cutting-edge technologies and make a significant impact on our products and services.

## Key Responsibilities

{chr(10).join([f"- {resp}" for resp in responsibility_set[:6]])}

## Required Qualifications

{chr(10).join([f"- {qual}" for qual in qualification_set[:6]])}

## Preferred Skills

{chr(10).join([f"- {skill}" for skill in preferred_set[:6]])}

## What We Offer

{chr(10).join([f"- {benefit}" for benefit in benefit_set[:6]])}

## Company Culture

We foster an inclusive, diverse, and innovative workplace where every team member's contribution is valued. Our culture emphasizes:

- **Innovation**: Encouraging creative thinking and experimentation
- **Collaboration**: Working together to achieve common goals  
- **Growth**: Continuous learning and professional development
- **Impact**: Making a meaningful difference in our industry
- **Excellence**: Striving for the highest quality in everything we do

## Application Process

If you're excited about this opportunity and meet the qualifications, we'd love to hear from you. Please submit your application with:

- Updated resume highlighting relevant experience
- Cover letter explaining your interest in the role
- Portfolio or examples of your work (if applicable)

Join our team and be part of building the future of technology! We're looking forward to welcoming a talented {designation} to our growing team in {location}.

---

*We are an equal opportunity employer committed to diversity and inclusion. All qualified applicants will receive consideration for employment without regard to race, color, religion, sex, sexual orientation, gender identity, national origin, disability, or veteran status.*
"""
    
    return jd

def generate_ai_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Generates job description using Hugging Face AI model.
    """
    skills_text = ", ".join(skills) if skills else "relevant technical skills"
    department = department or "Technology"
    
    # Create a focused prompt for better AI generation
    prompt = f"""Job Title: {designation}
Department: {department}
Location: {location}
Experience: {experience}+ years
Skills: {skills_text}

Job Description:
We are seeking a {designation} to join our {department} team in {location}. The ideal candidate will have {experience}+ years of experience with {skills_text}.

Key Responsibilities:
- Design and develop software solutions
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Troubleshoot and debug applications
- Stay current with technology trends

Required Qualifications:
- {experience}+ years of software development experience
- Strong proficiency in {skills_text}
- Bachelor's degree in Computer Science or related field
- Experience with version control systems
- Strong problem-solving skills
- Excellent communication abilities

What We Offer:
- Competitive salary and benefits
- Flexible working arrangements
- Professional development opportunities
- Collaborative work environment
- Health and wellness programs
- Modern technology stack

Join our team and help build innovative solutions!"""

    try:
        generator = get_optimized_generator()
        if generator is None:
            print("AI model not available, using template fallback")
            return generate_fast_ai_jd(designation, experience, location, skills, department)
        
        # Generate with AI model
        response = generator(
            prompt,
            max_new_tokens=300,  # Reasonable length for job description
            num_return_sequences=1,
            do_sample=True,
            temperature=0.8,  # Good balance of creativity and coherence
            top_p=0.9,
            pad_token_id=50256,
            truncation=True,
            return_full_text=False  # Only return the generated part
        )
        
        generated_text = response[0]["generated_text"]
        
        # Clean up the generated text
        generated_text = generated_text.strip()
        
        # If the response is too short or doesn't look good, use fallback
        if len(generated_text) < 200 or "Job Title:" in generated_text:
            print("AI generation too short, using template fallback")
            return generate_fast_ai_jd(designation, experience, location, skills, department)
        
        # Post-process for better formatting
        generated_text = post_process_jd(generated_text)
        
        return generated_text
        
    except Exception as e:
        print(f"AI generation error: {e}")
        return generate_fast_ai_jd(designation, experience, location, skills, department)

def generate_jd_ultimate(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Generates a comprehensive job description using AI model with fallback.
    """
    print("Using AI model for job description generation")
    return generate_ai_jd(designation, experience, location, skills, department)

def post_process_jd(text: str) -> str:
    """Post-process the generated job description for better formatting"""
    # Ensure proper markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)  # Fix bold formatting
    text = re.sub(r'^(\d+\.\s)', r'### \1', text, flags=re.MULTILINE)  # Convert numbered lists to headers
    text = re.sub(r'^-\s', '- ', text, flags=re.MULTILINE)  # Ensure consistent bullet points
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive line breaks
    text = text.strip()
    
    return text

def create_ultimate_fallback_jd(designation: str, experience: int, location: str, skills: list = None, department: str = None) -> str:
    """
    Creates an enhanced fallback job description when AI generation fails.
    This is more comprehensive than the basic fallback.
    """
    skills_text = ", ".join(skills) if skills else "relevant technical skills"
    
    return f"""# {designation}

**Department:** {department or "Technology"}  
**Location:** {location}  
**Experience Required:** {experience}+ years  
**Employment Type:** Full-time

## Job Summary

We are seeking a highly skilled and experienced {designation} to join our innovative team in {location}. The ideal candidate will bring {experience}+ years of expertise in {skills_text} and demonstrate a passion for delivering exceptional results in a fast-paced, collaborative environment.

As a {designation}, you will play a crucial role in driving our technology initiatives forward while contributing to our company's growth and success. This position offers an excellent opportunity to work with cutting-edge technologies and make a significant impact on our products and services.

## Key Responsibilities

- **Technical Leadership**: Lead and contribute to the design, development, and implementation of high-quality software solutions
- **Project Management**: Collaborate with cross-functional teams to define project requirements, timelines, and deliverables
- **Code Quality**: Write clean, maintainable, and well-documented code following industry best practices
- **Problem Solving**: Analyze complex technical challenges and develop innovative solutions
- **Mentorship**: Guide and mentor junior team members, fostering a culture of continuous learning
- **Innovation**: Stay current with emerging technologies and industry trends, recommending improvements
- **Collaboration**: Work closely with product managers, designers, and other stakeholders to deliver exceptional user experiences
- **Quality Assurance**: Participate in code reviews, testing, and quality assurance processes

## Required Qualifications

- **Experience**: {experience}+ years of professional experience in software development or related field
- **Technical Skills**: Strong proficiency in {skills_text}
- **Education**: Bachelor's degree in Computer Science, Engineering, or equivalent practical experience
- **Version Control**: Extensive experience with Git and collaborative development workflows
- **Problem-Solving**: Demonstrated ability to analyze complex problems and develop effective solutions
- **Communication**: Excellent verbal and written communication skills
- **Teamwork**: Proven ability to work effectively in collaborative, cross-functional teams
- **Adaptability**: Strong ability to learn new technologies and adapt to changing requirements

## Preferred Skills

- **Cloud Platforms**: Experience with AWS, Azure, or Google Cloud Platform
- **DevOps**: Knowledge of CI/CD pipelines, containerization (Docker), and infrastructure as code
- **Agile Methodologies**: Experience with Scrum, Kanban, or other agile development practices
- **Testing**: Proficiency with unit testing, integration testing, and test-driven development
- **Database Technologies**: Experience with SQL and NoSQL databases
- **Security**: Understanding of application security best practices
- **Leadership**: Previous experience leading technical projects or mentoring team members

## What We Offer

- **Competitive Compensation**: Attractive salary package with performance-based bonuses
- **Comprehensive Benefits**: Health, dental, and vision insurance with company contributions
- **Flexible Work Arrangements**: Remote work options and flexible scheduling
- **Professional Development**: Access to training programs, conferences, and certification opportunities
- **Career Growth**: Clear advancement paths and opportunities for skill development
- **Modern Technology Stack**: Work with the latest tools and technologies
- **Collaborative Culture**: Supportive team environment that values innovation and creativity
- **Work-Life Balance**: Generous PTO policy and employee wellness programs
- **Stock Options**: Equity participation in our growing company
- **Learning Budget**: Annual allowance for books, courses, and professional development

## Company Culture

We foster an inclusive, diverse, and innovative workplace where every team member's contribution is valued. Our culture emphasizes:

- **Innovation**: Encouraging creative thinking and experimentation
- **Collaboration**: Working together to achieve common goals
- **Growth**: Continuous learning and professional development
- **Impact**: Making a meaningful difference in our industry
- **Excellence**: Striving for the highest quality in everything we do

## Application Process

If you're excited about this opportunity and meet the qualifications, we'd love to hear from you. Please submit your application with:

- Updated resume highlighting relevant experience
- Cover letter explaining your interest in the role
- Portfolio or examples of your work (if applicable)

Join our team and be part of building the future of technology! We're looking forward to welcoming a talented {designation} to our growing team in {location}.

---

*We are an equal opportunity employer committed to diversity and inclusion. All qualified applicants will receive consideration for employment without regard to race, color, religion, sex, sexual orientation, gender identity, national origin, disability, or veteran status.*
"""
