# AI_Resume_Analysis_Backend (TalentFitAI)

TalentFitAI is a comprehensive HR management system that leverages AI to generate job descriptions and manage the complete recruitment workflow. The system allows HR managers to create job requisitions, generate AI-powered job descriptions, and publish job posts to various external portals.

## 🚀 Features

### 1. **HR Manager Authentication**
- Secure user registration and login
- JWT-based authentication

### 2. **Job Requisition Management**
- Create detailed job requisitions with requirements
- Define skills, experience, and qualifications
- Set salary ranges and employment types
- Full CRUD operations for requisitions

### 3. **AI-Powered Job Description Generation**
- Uses free AI models from Hugging Face (Microsoft DialoGPT)
- Generates professional, LinkedIn-style job descriptions
- Fallback templates for reliable output
- Customizable prompts for different roles

### 4. **Job Post Publishing**
- Convert requisitions to job posts
- AI-generated job descriptions
- Simulated publishing to external portals (LinkedIn, Naukri, Indeed)
- Track external job IDs and publishing status

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/ML**: Hugging Face Transformers
- **Authentication**: JWT with bcrypt password hashing
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/priyaranirai-sdn/AI_Resume_Analysis_Backend.git
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database
```bash
# Make sure PostgreSQL is running
# Update database credentials in app/models/database.py if needed
python setup_database.py
```

### 5. Run the Application
```bash
py start_server.py
```

### 5. Access the Application
- **API Documentation**: http://localhost:9142/docs
- **Alternative Docs**: http://localhost:9142/redoc
- **Health Check**: http://localhost:9142/health

## 📚 API Documentation

### Authentication Endpoints

#### Register HR Manager
```http
POST /auth/register
Content-Type: application/json

{
  "email": "hr@company.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "hr@company.com",
  "password": "securepassword"
}
```

### Requisition Management

#### Create Requisition
```http
POST /requisition/
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "department": "Engineering",
  "location": "San Francisco, CA",
  "experience_required": 5,
  "skills_required": ["Python", "FastAPI", "React", "AWS"],
  "responsibilities": "Lead development of microservices...",
  "qualifications": "Bachelor's degree in Computer Science...",
  "salary_range_min": 120000,
  "salary_range_max": 150000,
  "employment_type": "Full-time"
}
```

#### Get All Requisitions
```http
GET /requisition/
Authorization: Bearer <your-jwt-token>
```

#### Update Requisition
```http
PUT /requisition/{requisition_id}
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "status": "Approved",
  "salary_range_min": 130000
}
```

### Job Post Management

#### Create Job Post from Requisition
```http
POST /job-post/
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "requisition_id": 1,
  "expires_in_days": 30
}
```

#### Publish Job Post to External Portals
```http
POST /job-post/{job_post_id}/publish
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "portals": ["linkedin", "naukri", "indeed"]
}
```

#### Regenerate Job Description
```http
POST /job-post/{job_post_id}/regenerate-description
Authorization: Bearer <your-jwt-token>
```



# Resume Analysis API Documentation

## Overview

The Resume Analysis API provides AI-powered resume matching against job descriptions. It supports multiple file formats (PDF, DOC, DOCX) and provides detailed analysis including match percentages, skill gaps, and suitability ratings.

## Features

- **Multi-format Support**: PDF, DOC, DOCX files
- **AI-powered Analysis**: Uses Hugging Face models for text similarity and skill matching
- **Detailed Reports**: Comprehensive analysis with match percentages, confidence scores, and gap analysis
- **Bulk Processing**: Analyze multiple resumes at once
- **Case-insensitive Matching**: Skills matching is not case-sensitive
- **Domain Agnostic**: Works for technical and non-technical roles

## API Endpoints

### 1. Analyze Single Resume

**POST** `/resume-analysis/analyze`

Analyze a single resume against a job requisition.

#### Request
- **Content-Type**: `multipart/form-data`
- **Authentication**: Required (Bearer token)

#### Parameters
- `requisition_id` (int, required): ID of the job requisition
- `candidate_name` (string, required): Name of the candidate
- `resume_file` (file, required): Resume file (PDF, DOC, or DOCX)

#### Response
```json
{
  "id": 1,
  "requisition_id": 1,
  "candidate_name": "John Doe",
  "resume_filename": "john_doe_resume.pdf",
  "match_percentage": 85.5,
  "confidence_score": 78.2,
  "is_match": "Match",
  "skills_match": {
    "matched_skills": ["React", "JavaScript", "Node.js"],
    "missing_skills": ["MongoDB", "AWS"],
    "match_percentage": 60.0
  },
  "missing_skills": ["MongoDB", "AWS"],
  "experience_match": true,
  "gaps_analysis": "Missing required skills: MongoDB, AWS",
  "suitability_rating": "High",
  "analysis_details": {
    "resume_experience": 4,
    "required_experience": 3,
    "resume_skills": ["React", "JavaScript", "Node.js", "Python"]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Analyze Multiple Resumes (Bulk)

**POST** `/resume-analysis/analyze-bulk`

Analyze multiple resumes against a job requisition in a single request.

#### Request
- **Content-Type**: `multipart/form-data`
- **Authentication**: Required (Bearer token)

#### Parameters
- `requisition_id` (int, required): ID of the job requisition
- `resume_files` (array of files, required): Multiple resume files
- `candidate_names` (string, required): JSON array of candidate names

#### Response
```json
{
  "total_candidates": 3,
  "matches": 2,
  "partial_matches": 1,
  "not_matches": 0,
  "candidates": [
    {
      "id": 1,
      "candidate_name": "Alice Johnson",
      "match_percentage": 92.0,
      "is_match": "Match",
      "suitability_rating": "High"
    },
    {
      "id": 2,
      "candidate_name": "Bob Smith",
      "match_percentage": 65.0,
      "is_match": "Partial Match",
      "suitability_rating": "Medium"
    }
  ]
}
```

### 3. Get Resume Analyses for Requisition

**GET** `/resume-analysis/requisition/{requisition_id}`

Retrieve all resume analyses for a specific requisition, ordered by match percentage.

#### Response
Array of resume analysis objects (same format as single analysis).

### 4. Get Specific Analysis

**GET** `/resume-analysis/analysis/{analysis_id}`

Retrieve a specific resume analysis by ID.

#### Response
Single resume analysis object.

### 5. Get Analysis Summary

**GET** `/resume-analysis/summary/{requisition_id}`

Get a summary of all analyses for a requisition.

#### Response
```json
{
  "total_candidates": 5,
  "matches": 2,
  "partial_matches": 2,
  "not_matches": 1,
  "average_match_percentage": 75.4,
  "top_candidates": [
    {
      "candidate_name": "Alice Johnson",
      "match_percentage": 92.0,
      "is_match": "Match",
      "suitability_rating": "High"
    }
  ]
}
```

### 6. Delete Analysis

**DELETE** `/resume-analysis/analysis/{analysis_id}`

Delete a specific resume analysis.

#### Response
```json
{
  "message": "Resume analysis deleted successfully"
}
```

## Analysis Details

### Match Categories
- **Match**: 80%+ overall match
- **Partial Match**: 60-79% overall match
- **Not a Match**: <60% overall match

### Suitability Ratings
- **High**: Strong match with most requirements met
- **Medium**: Partial match with some gaps
- **Low**: Poor match with significant gaps

### Scoring Algorithm
The overall match percentage is calculated using:
- **40%** Skills match percentage
- **30%** Experience requirement match
- **30%** Content similarity (AI-powered)

### Skills Matching
- Case-insensitive matching
- Partial string matching (e.g., "React" matches "React.js")
- Supports technical and non-technical skills
- Extracts skills from various resume sections

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Only PDF, DOC, and DOCX files are supported"
}
```

#### 404 Not Found
```json
{
  "detail": "Requisition not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Error analyzing resume: [error message]"
}
```

## Usage Examples

### Python Example

```python
import requests

# Analyze single resume
files = {"resume_file": ("resume.pdf", open("resume.pdf", "rb"), "application/pdf")}
data = {
    "requisition_id": 1,
    "candidate_name": "John Doe"
}

response = requests.post(
    "http://localhost:9142/resume-analysis/analyze",
    files=files,
    data=data,
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)

result = response.json()
print(f"Match: {result['match_percentage']}%")
```

### JavaScript Example

```javascript
const formData = new FormData();
formData.append('resume_file', fileInput.files[0]);
formData.append('requisition_id', '1');
formData.append('candidate_name', 'John Doe');

fetch('http://localhost:9142/resume-analysis/analyze', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## File Format Support

### Supported Formats
- **PDF**: `.pdf` files
- **Microsoft Word**: `.doc` and `.docx` files

### File Size Limits
- Maximum file size: 10MB per file
- Maximum files per bulk request: 20

## AI Models Used

- **Text Similarity**: `sentence-transformers/all-MiniLM-L6-v2`
- **Feature Extraction**: Hugging Face Transformers
- **Text Classification**: `microsoft/DialoGPT-medium`

## Database Schema

### ResumeAnalysis Table
- `id`: Primary key
- `requisition_id`: Foreign key to requisitions table
- `candidate_name`: Name of the candidate
- `resume_filename`: Original filename
- `resume_content`: Extracted text content
- `match_percentage`: Overall match percentage
- `confidence_score`: AI confidence score
- `is_match`: Match status (Match/Partial Match/Not a Match)
- `skills_match`: JSON object with skills analysis
- `missing_skills`: Array of missing required skills
- `experience_match`: Boolean for experience requirement
- `gaps_analysis`: Text description of gaps
- `suitability_rating`: High/Medium/Low rating
- `analysis_details`: JSON object with detailed analysis
- `created_at`: Timestamp
- `created_by`: Foreign key to users table

## Security

- All endpoints require authentication
- Users can only access analyses for their own requisitions
- File uploads are validated for type and size
- Sensitive data is not logged

## Rate Limiting

- Single analysis: No specific limits
- Bulk analysis: Maximum 20 files per request
- API calls: Standard rate limiting applies

## Troubleshooting

### Common Issues

1. **File Upload Errors**
   - Ensure file format is supported (PDF, DOC, DOCX)
   - Check file size (max 10MB)
   - Verify file is not corrupted

2. **Analysis Errors**
   - Ensure requisition exists and belongs to user
   - Check that job post exists for requisition
   - Verify file contains extractable text

3. **Low Match Percentages**
   - Check if skills in resume match required skills
   - Verify experience requirements are met
   - Ensure resume contains relevant content

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
```

## Support

For technical support or questions about the Resume Analysis API, please contact the development team or refer to the main API documentation.
