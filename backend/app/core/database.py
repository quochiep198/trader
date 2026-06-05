from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

db_url = settings.sqlalchemy_database_url

# Setup connection parameters based on DB driver (SQLite vs PostgreSQL/Neon)
if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url, 
        connect_args={"check_same_thread": False}
    )
else:
    # Neon Serverless Postgres optimization parameters
    engine = create_engine(
        db_url, 
        pool_size=5, 
        max_overflow=10,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get db session in API router endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
