import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
import streamlit as st

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with proper SSL settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create session factory
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

# Create tables
def init_db():
    try:
        # Test connection with proper SQL execution
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()