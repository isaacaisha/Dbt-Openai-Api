import pytest
from app import models


@pytest.fixture()
def test_vote(test_conversations, session, test_user):
    new_vote = models.Vote(post_id=test_conversations[2].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


# url: pytest tests/test_vote.py::test_vote_conversation -v -s
def test_vote_conversation(authorized_client, test_conversations):
    response = authorized_client.post("/vote/", json={"post_id": test_conversations[0].id, "dir": 1})
    assert response.status_code == 201


# url: pytest tests/test_vote.py::test_vote_twice_conversation -v -s
def test_vote_twice_conversation(authorized_client, test_conversations, test_vote):
    response = authorized_client.post("/vote/", json={"post_id": test_conversations[2].id, "dir": 1})
    assert response.status_code == 409


# url: pytest tests/test_vote.py::test_delete_vote -v -s
def test_delete_vote(authorized_client, test_conversations, test_vote):
    response = authorized_client.post("/vote/", json={"post_id": test_conversations[2].id, "dir": 0})
    assert response.status_code == 201


# url: pytest tests/test_vote.py::test_delete_vote_not_found -v -s
def test_delete_vote_not_found(authorized_client, test_conversations):
    response = authorized_client.post("/vote/", json={"post_id": test_conversations[2].id, "dir": 0})
    assert response.status_code == 404


# url: pytest tests/test_vote.py::test_vote_conversation_not_found -v -s
def test_vote_conversation_not_found(authorized_client, test_conversations):
    response = authorized_client.post("/vote/", json={"post_id": 991, "dir": 1})
    assert response.status_code == 404


# url: pytest tests/test_vote.py::test_vote_unauthorized_user -v -s
def test_vote_unauthorized_user(client, test_conversations):
    response = client.post("/vote/", json={"post_id": test_conversations[1].id, "dir": 1})
    assert response.status_code == 401
    