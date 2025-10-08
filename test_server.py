#!/usr/bin/env python3
"""
Test script for TalentFitAI Backend Server
"""

import requests
import json
import sys

def test_server():
    """Test the server endpoints"""
    base_url = "http://localhost:9142"
    
    print("🧪 Testing TalentFitAI Backend Server...")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
        # Test docs endpoint
        print("\n3. Testing docs endpoint...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Docs endpoint accessible")
        else:
            print(f"❌ Docs endpoint failed: {response.status_code}")
            
        print("\n🎉 All basic tests passed!")
        print("📚 API Documentation: http://localhost:9142/docs")
        print("🔍 Alternative Docs: http://localhost:9142/redoc")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        print("💡 Try running: python start_server.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
