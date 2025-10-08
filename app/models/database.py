from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL - using PostgreSQL
# Default PostgreSQL connection string - update with your credentials
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://talentfitai:JDG7uyjhgd5VHA@54.201.160.69:5432/talentfitai"
)


# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://test:test@localhost:5432/mydb"
# )

# Create engine with PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
