#!/usr/bin/env python3
"""
Database setup script for TalentFitAI
This script creates the PostgreSQL database and tables.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from app.models.database import DATABASE_URL, engine
from app.models import create_tables

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    
    # Parse the DATABASE_URL to get connection details
    # Format: postgresql://username:password@host:port/database
    url_parts = DATABASE_URL.replace("postgresql://", "").split("/")
    db_name = url_parts[1]
    connection_part = url_parts[0].split("@")
    
    if len(connection_part) == 2:
        user_pass = connection_part[0].split(":")
        username = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        host_port = connection_part[1].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
    else:
        # Default values if parsing fails
        username = "postgres"
        password = "password"
        host = "172.10.3.17"
        port = 5432
    
    print(f"🔧 Setting up PostgreSQL database...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Username: {username}")
    print(f"   Database: {db_name}")
    
    try:
        # Connect to PostgreSQL server (not to the specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📦 Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created successfully!")
        else:
            print(f"✅ Database '{db_name}' already exists!")
        
        cursor.close()
        conn.close()
        
        # Create tables
        print(f"📋 Creating tables...")
        create_tables()
        print(f"✅ Tables created successfully!")
        
        print(f"\n🎉 Database setup completed!")
        print(f"   You can now run: uvicorn app.main:app --reload")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print(f"\n🔧 Please ensure:")
        print(f"   1. PostgreSQL is running")
        print(f"   2. Username and password are correct")
        print(f"   3. PostgreSQL is accessible on {host}:{port}")
        print(f"\n💡 Default connection string: postgresql://postgres:password@localhost:5432/talentfitai")
        print(f"   Update DATABASE_URL in app/models/database.py if needed")
        print(f"\n📋 Manual setup steps:")
        print(f"   1. Open pgAdmin")
        print(f"   2. Connect to PostgreSQL server")
        print(f"   3. Create database named 'talentfitai'")
        print(f"   4. Update password in app/models/database.py")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    create_database()
