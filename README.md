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
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

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