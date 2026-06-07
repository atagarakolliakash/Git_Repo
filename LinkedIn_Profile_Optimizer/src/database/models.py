"""Database configuration and models for LinkedIn Agent."""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./linkedin_agent.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """LinkedIn user profile information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    linkedin_id = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    headline = Column(String)
    about = Column(Text)
    profile_pic_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Experience(Base):
    """User's job experience and responsibilities."""
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    key_responsibilities = Column(Text)  # Parsed responsibilities
    skills_used = Column(Text)  # Comma-separated skills
    achievements = Column(Text)  # Parsed achievements
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedContent(Base):
    """AI-generated content for posting."""
    __tablename__ = "generated_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content = Column(Text)
    content_type = Column(String)  # insight, tip, achievement, question, etc.
    status = Column(String, default="pending")  # pending, scheduled, posted, failed
    source_experience_id = Column(Integer)  # Which experience this was based on
    generated_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)
    engagement_score = Column(Float, default=0.0)


class Post(Base):
    """Posted content tracking."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content_id = Column(Integer, index=True)
    linkedin_post_id = Column(String, unique=True)
    content = Column(Text)
    posted_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EngagementMetric(Base):
    """Engagement metrics tracking."""
    __tablename__ = "engagement_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    post_id = Column(Integer, index=True)
    metric_date = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)


class ScheduleLog(Base):
    """Task scheduling logs."""
    __tablename__ = "schedule_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    task_name = Column(String)
    task_type = Column(String)  # generate, post, analyze, etc.
    status = Column(String)  # success, failure, pending
    message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
