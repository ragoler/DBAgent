import os
import logging
from typing import Dict, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# ContextVar to track the active database ID for the current request/task
database_context_var: ContextVar[Optional[str]] = ContextVar("database_id", default=None)

# Registry of engines: db_id -> Engine
_engines: Dict[str, Engine] = {}
_session_makers: Dict[str, sessionmaker] = {}

# Create Base class for declarative models
Base = declarative_base()

def register_database(db_id: str, db_url: str):
    """
    Registers a new database engine.
    """
    logger.info(f"Registering database '{db_id}' with URL: {db_url}")
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
        echo=False  # Set to True for verbose SQL logging
    )
    _engines[db_id] = engine
    _session_makers[db_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine(db_id: Optional[str] = None) -> Engine:
    """
    Returns the SQLAlchemy engine for the specified or active database.
    """
    if db_id is None:
        db_id = database_context_var.get()
    
    if not db_id or db_id not in _engines:
        # Fallback to the first registered engine if only one exists (backward compatibility)
        if len(_engines) == 1:
            return next(iter(_engines.values()))
        raise ValueError(f"No active database context and no default found. (Context: {db_id})")
    
    return _engines[db_id]

def get_session(db_id: Optional[str] = None) -> Session:
    """
    Returns a new synchronous database session for the active database.
    """
    if db_id is None:
        db_id = database_context_var.get()
        
    if not db_id or db_id not in _session_makers:
         # Fallback logic for single-DB setup
        if len(_session_makers) == 1:
            return next(iter(_session_makers.values()))()
        raise ValueError(f"Cannot create session: Database ID '{db_id}' not registered.")

    return _session_makers[db_id]()

def get_db():
    """Dependency for getting a database session (fastapi style)."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()
