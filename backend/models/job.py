from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://autodevos:devpass123@localhost:5432/autodevos")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    prompt = Column(Text)
    status = Column(String, default="queued")  # queued, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    iterations = Column(Integer, default=0)
    current_iteration = Column(Integer, default=0)
    overall_reward = Column(Float, default=0.0)
    codebase = Column(JSON, default={})  # filename -> content
    meeting_log = Column(JSON, default=[])
    error_message = Column(Text, nullable=True)


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    iteration = Column(Integer)
    agent = Column(String)  # pm, architect, developer, qa, security, tech_debt, seo
    score = Column(Float)  # 0-10
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
