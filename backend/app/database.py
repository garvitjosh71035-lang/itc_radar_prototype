"""
Database connection and session management.
Implements Section 15 data model from workflow.md.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine with PostGIS support
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,           # Test connections before use
    pool_size=10,                 # Connection pool size
    max_overflow=20,              # Maximum overflow connections
    pool_timeout=30,              # Seconds to wait for connection
    echo=settings.DEBUG,          # Log SQL queries in debug mode
)

# Session factory
LocalSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    Usage in FastAPI:
        @app.get("/cases")
        def list_cases(db: Session = Depends(get_db)):
            # Use db session
    """
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Called on first startup or via Alembic migrations.
    """
    # Import models here to avoid circular imports
    from app.models import Registration, InvoiceLine, PremisesCluster
    # All models are imported - Base.metadata.create_all(engine) creates them
    
    # Add PostGIS extension if not present
    with engine.connect() as conn:
        try:
            conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            conn.commit()
        except Exception as e:
            print(f"Warning: Could not create PostGIS extension: {e}")


class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass


def check_connection() -> bool:
    """
    Check if database connection is working.
    Used for health checks and deployment validation.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
