import re
from transformers import pipeline

# Load a conversational/text-generation model
generator = pipeline("text-generation", model="microsoft/DialoGPT-medium")

def generate_screening_questions(job_description: str, num_questions: int = 5) -> dict:
    """
    Generate screening questions from a job description using AI.

    Args:
        job_description: Full job description text.
        num_questions: Number of screening questions to generate.

    Returns:
        Dictionary of screening questions in the format:
        {
            "q1": "First question",
            "q2": "Second question",
            ...
        }
    """
    prompt = f"""
Based on the following job description, create {num_questions} relevant screening questions 
for candidates. Include a mix of technical and behavioral questions where appropriate.

Job Description:
{job_description}

Screening Questions:
1."""
    
    try:
        response = generator(
            prompt,
            max_new_tokens=256,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            pad_token_id=generator.tokenizer.eos_token_id,
            truncation=True
        )
        
        generated_text = response[0]["generated_text"]

        # Extract numbered questions using regex
        questions = []
        matches = re.findall(r'\d+\.\s*(.*)', generated_text)
        for q in matches:
            question = q.strip()
            if question:
                questions.append(question)
        
        # fallback in case AI fails
        if not questions:
            questions = create_fallback_questions(job_description, num_questions)
        
        # Convert to numbered dictionary format
        numbered_questions = {f"q{i+1}": q for i, q in enumerate(questions[:num_questions])}
        
        return numbered_questions

    except Exception as e:
        print(f"Error generating screening questions: {e}")
        questions = create_fallback_questions(job_description, num_questions)
        return {f"q{i+1}": q for i, q in enumerate(questions)}
    
    
def create_fallback_questions(job_description: str, num_questions: int = 5) -> list:
    """
    Simple fallback: generate generic questions based on job description keywords.
    """
    fallback_questions = [
        "Describe your experience relevant to this role.",
        "What challenges have you faced in similar positions?",
        "Which skills from this job description do you excel at?",
        "How would you approach a project in this role?",
        "Why are you interested in this position?"
    ]
    return fallback_questions[:num_questions]

# Example usage
jd_text = """We are seeking a talented Python Developer with 3+ years of experience in web development, REST APIs, and cloud platforms. The ideal candidate should be familiar with Django, Flask, AWS, and agile methodologies."""
questions = generate_screening_questions(jd_text, num_questions=5)
for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")
