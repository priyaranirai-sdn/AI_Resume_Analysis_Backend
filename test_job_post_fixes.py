#!/usr/bin/env python3
"""
Test script to verify job post endpoint fixes and AI model performance
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

def test_ai_health():
    """Test AI model health endpoint"""
    print("🔍 Testing AI Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/job-post/health/ai", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"AI Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Load Time: {data.get('load_time', 'N/A')} seconds")
            print(f"Test Generation Time: {data.get('test_generation_time', 'N/A')} seconds")
            return data.get('status') == 'healthy'
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing AI health: {e}")
        return False

def create_test_user():
    """Create a test user for authentication"""
    print("👤 Creating test user...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 200:
            print("✅ Test user created successfully")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("ℹ️  Test user already exists")
            return True
        else:
            print(f"❌ Failed to create user: {response.text}")
            return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def login_user():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def create_test_requisition(token):
    """Create a test requisition"""
    print("📝 Creating test requisition...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        requisition_data = {
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "San Francisco, CA",
            "experience_required": 5,
            "skills_required": ["Python", "FastAPI", "React", "PostgreSQL"],
            "salary_range_min": 120000,
            "salary_range_max": 180000,
            "employment_type": "Full-time"
        }
        
        response = requests.post(f"{BASE_URL}/requisition/", json=requisition_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Requisition created with ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Failed to create requisition: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating requisition: {e}")
        return None

def test_job_post_creation(token, requisition_id):
    """Test job post creation with AI generation"""
    print("🚀 Testing job post creation...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        job_post_data = {
            "requisition_id": requisition_id,
            "expires_in_days": 30
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/job-post/", json=job_post_data, headers=headers, timeout=60)
        end_time = time.time()
        
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Job post created successfully!")
            print(f"Job Post ID: {data.get('id')}")
            print(f"Title: {data.get('title')}")
            print(f"Description Length: {len(data.get('description', ''))} characters")
            print(f"Location: {data.get('location')}")
            print(f"Experience Required: {data.get('experience_required')} years")
            return True
        else:
            print(f"❌ Job post creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error creating job post: {e}")
        return False

def test_error_handling(token):
    """Test error handling with invalid data"""
    print("⚠️  Testing error handling...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with invalid requisition ID
        job_post_data = {
            "requisition_id": 99999,  # Non-existent ID
            "expires_in_days": 30
        }
        
        response = requests.post(f"{BASE_URL}/job-post/", json=job_post_data, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Error handling working correctly - 404 for non-existent requisition")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing error handling: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Starting Job Post Endpoint Tests")
    print("=" * 50)
    
    # Test 1: AI Health Check
    ai_healthy = test_ai_health()
    print()
    
    # Test 2: User Authentication
    if not create_test_user():
        print("❌ Cannot proceed without test user")
        return
    
    token = login_user()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    print()
    
    # Test 3: Create Test Requisition
    requisition_id = create_test_requisition(token)
    if not requisition_id:
        print("❌ Cannot proceed without test requisition")
        return
    print()
    
    # Test 4: Job Post Creation
    job_post_success = test_job_post_creation(token, requisition_id)
    print()
    
    # Test 5: Error Handling
    error_handling_success = test_error_handling(token)
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    print(f"AI Model Health: {'✅ PASS' if ai_healthy else '❌ FAIL'}")
    print(f"Job Post Creation: {'✅ PASS' if job_post_success else '❌ FAIL'}")
    print(f"Error Handling: {'✅ PASS' if error_handling_success else '❌ FAIL'}")
    
    if ai_healthy and job_post_success and error_handling_success:
        print("\n🎉 All tests passed! The fixes are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
