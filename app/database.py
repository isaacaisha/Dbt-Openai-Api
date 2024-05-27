from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings


# Construct the SQLALCHEMY_DATABASE_URL using the settings
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.admin_user}:{settings.admin_password}@{settings.admin_host}:{settings.admin_port}/{settings.admin_database}"
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
