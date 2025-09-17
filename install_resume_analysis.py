#!/usr/bin/env python3
"""
Installation script for Resume Analysis dependencies
Run this script to install the required packages for resume analysis functionality
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages for resume analysis"""
    
    packages = [
        "PyPDF2==3.0.1",
        "python-docx==1.1.0", 
        "scikit-learn==1.3.2",
        "numpy==1.24.3",
        "sentence-transformers==2.2.2"
    ]
    
    print("🔧 Installing Resume Analysis Dependencies")
    print("=" * 50)
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e}")
            return False
    
    print("\n🎉 All packages installed successfully!")
    print("\nNext steps:")
    print("1. Run the database migration to create the resume_analyses table")
    print("2. Start the server with: python start_server.py")
    print("3. Test the API using the test_resume_analysis.py script")
    
    return True

def create_database_migration():
    """Create a simple database migration script"""
    
    migration_script = '''
# Database Migration for Resume Analysis
# Run this script to create the resume_analyses table

from app.models import create_tables

if __name__ == "__main__":
    print("Creating resume_analyses table...")
    create_tables()
    print("✅ Database migration completed!")
'''
    
    with open("migrate_resume_analysis.py", "w") as f:
        f.write(migration_script)
    
    print("📄 Created migration script: migrate_resume_analysis.py")

if __name__ == "__main__":
    print("Resume Analysis Setup")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Warning: Not in a virtual environment. Consider using a virtual environment.")
    
    # Install packages
    if install_packages():
        create_database_migration()
        
        print("\n📋 Installation Summary:")
        print("- PyPDF2: PDF text extraction")
        print("- python-docx: Word document text extraction") 
        print("- scikit-learn: Machine learning utilities")
        print("- numpy: Numerical computing")
        print("- sentence-transformers: Text similarity models")
        
        print("\n🚀 Ready to analyze resumes!")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
