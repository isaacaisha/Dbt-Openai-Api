import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models

load_dotenv()


# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:Toure7Medina@localhost:5433/siisi_api_test'
# Construct the SQLALCHEMY_DATABASE_URL using the settings
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.admin_user}:{settings.admin_password}@{settings.admin_host}:{settings.admin_port}/{settings.admin_database}_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user2(client):
    user_data = {"email": "dbt2@dbt2.com", "password": "dbt2","name": "dbt2"}
    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    print(response.json())
    new_user = response.json()
    new_user['password'] = user_data["password"]
    return new_user


@pytest.fixture
def test_user(client):
    user_data = {"email": "dbt@dbt.com", "password": "dbt","name": "dbt"}
    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    print(response.json())
    new_user = response.json()
    new_user['password'] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


# @pytest.fixture()
# def auth_headers(client):
#     # Create a test user and get an auth token
#     user_data = {"email": "testuser@example.com", "password": "testpassword", "name": "Test User"}
#     client.post("/users/", json=user_data)
#     response = client.post("/login", data={"username": user_data["email"], "password": user_data["password"]})
#     token = response.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}
#     print('')
#     return headers


@pytest.fixture
def test_conversations(test_user, test_user2, session):
    conversation_data = [{
        "owner_id": test_user['id'],
        "user_message": "what can you tell me about the Muslim religion?",
        "llm_response": "string",
        "conversations_summary": "string",
        }, {
        "owner_id": test_user2['id'],
        "user_message": "what can you tell me about the Country named Indonesia?",
        "llm_response": "string",
        "conversations_summary": "string",
        }, {
        "owner_id": test_user['id'],
        "user_message": "what can you tell me about the Soninké people from Mali?",
        "llm_response": "string",
        "conversations_summary": "string",
        }]
    
    def create_conversation_model(conversation):
        return models.Memory(**conversation)
    
    conversation_map = map(create_conversation_model, conversation_data)
    conversations = list(conversation_map)
    session.add_all(conversations)
    session.commit()

    conversations = session.query(models.Memory).all()
    return conversations
