# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.main import app
# from app.config import settings
# from app.database import get_db, Base
# from dotenv import load_dotenv
# 
# 
# load_dotenv()
# 
# 
# # SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:Toure7Medina@localhost:5433/siisi_api_test'
# # Construct the SQLALCHEMY_DATABASE_URL using the settings
# SQLALCHEMY_DATABASE_URL = (
#     f"postgresql://{settings.admin_user}:{settings.admin_password}@{settings.admin_host}:{settings.admin_port}/{settings.admin_database}_test"
# )
# 
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# 
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 
# 
# @pytest.fixture()
# def session():
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# 
# 
# @pytest.fixture()
# def client(session):
#     def override_get_db():
#         try:
#             yield session
#         finally:
#             session.close()
#     app.dependency_overrides[get_db] = override_get_db
#     yield TestClient(app)
# 