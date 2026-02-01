import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get DB_URL from environment variable or default to local SQLite
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./test.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=True  # Log all SQL queries to the terminal
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

def get_engine():
    """Returns the SQLAlchemy engine."""
    return engine

def get_session():
    """Returns a new synchronous database session."""
    return SessionLocal()

def get_db():
    """Dependency for getting a database session (fastapi style)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
