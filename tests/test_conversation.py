import pytest
from app import schemas


# url: pytest tests/test_conversation.py::test_get_all_posts -v -s
def test_get_all_posts(authorized_client, test_conversations):
    response = authorized_client.get("/conversation/all")
    response_data = response.json()
    
    print(f"\nTest Conversations:\n{test_conversations}\n")
    print(f"Response Data:\n{response_data}\n")
    print(f"Response status code: {response.status_code}\n")

    assert response.status_code == 201
    assert len(response_data) == len(test_conversations)

    for i in range(len(test_conversations)):
        assert response_data[i]["user_message"] == test_conversations[i].user_message
        assert response_data[i]["llm_response"] == test_conversations[i].llm_response
        assert response_data[i]["conversations_summary"] == test_conversations[i].conversations_summary


# url: pytest tests/test_conversation.py::test_unauthorized_user_get_all_conversations -v -s
def test_unauthorized_user_get_all_conversations(client, test_conversations):
    response = client.get("/conversation/all")
    assert response.status_code == 401


# url: pytest tests/test_conversation.py::test_unauthorized_user_get_one_public_conversation -v -s
def test_unauthorized_user_get_one_public_conversation(client, test_conversations):
    conversation_id = test_conversations[1].id
    print(f"\nTesting unauthorized access to conversation ID: {conversation_id}\n")
    response = client.get(f"/conversation/get-public/{conversation_id}")
    print(f"Response status code: {response.status_code}\n")
    print(f"Response data: {response.json()}\n")
    assert response.status_code == 401



# url: pytest tests/test_conversation.py::test_unauthorized_user_get_one_private_conversation -v -s
def test_unauthorized_user_get_one_private_conversation(client, test_conversations):
    conversation_id = test_conversations[1].id
    print(f"\nTesting unauthorized access to conversation ID: {conversation_id}\n")
    response = client.get(f"/conversation/get-private/{conversation_id}")
    print(f"Response status code: {response.status_code}\n")
    print(f"Response data: {response.json()}\n")
    assert response.status_code == 401


# url: pytest tests/test_conversation.py::test_get_one_conversation_not_found -v -s
def test_get_one_conversation_not_found(authorized_client, test_conversations):
    non_existent_conversation_id = 991
    print(f"\nTesting access to non-existent conversation ID: {non_existent_conversation_id}\n")
    response = authorized_client.get(f"/conversation/get-public/{non_existent_conversation_id}")
    print(f"\nResponse status code: {response.status_code}\n")
    print(f"Response data: {response.json()}\n")
    assert response.status_code == 404


# url: pytest tests/test_conversation.py::test_get_one_conversation -v -s
def test_get_one_conversation(authorized_client, test_conversations):
    one_existent_conversation_id = test_conversations[2].id
    print(f"\nTesting access to one existent conversation ID: {one_existent_conversation_id}\n")
    response = authorized_client.get(f"/conversation/get-public/{one_existent_conversation_id}")
    print(f"Response status code: {response.status_code}\n")
    print(f"Response data: {response.json()}\n")
    assert response.status_code == 201

    conversation = schemas.MemoryResponse(**response.json())
    print(f'conversation:\n{conversation}\n')
    assert conversation.conversation_id == test_conversations[2].id
    print(f'test_conversations[2].user_message:\n{test_conversations[2].user_message}\n')
    assert conversation.user_message == test_conversations[2].user_message

    one_private_existent_conversation_id = test_conversations[0].id
    response = authorized_client.get(f"/conversation/get-private/{one_private_existent_conversation_id}")
    print(f"Response status code: {response.status_code}\n")
    print(f"Response data: {response.json()}\n")
    assert response.status_code == 201


# # url: pytest tests/test_conversation.py::test_start_interacting -v -s
# @pytest.mark.parametrize("user_message, llm_response, conversations_summary", [
#     ("who are You?", "string", "string"),
#     ("combien de langue parle tu?", "string", "string"),
#     # ("what can you tell me about the Muslim religion", "string", "string"),
#     # ("tell me about Python programming language", "string", "string"),
#     ("how do you say, how are you doing in Arabic?", "string", "string"),
#                          ])
# def test_start_interacting(authorized_client, test_user, test_conversations,
#                           user_message, llm_response, conversations_summary):
#     response = authorized_client.post("/conversation/start", json={
#         "user_message": user_message,
#         "llm_response": llm_response,
#         "conversations_summary": conversations_summary
#     })
#     # created_conversation = schemas.MemoryBase(**response.json())
#     # print(f'created_conversation:\n{created_conversation}')
#     assert response.status_code ==201


# URL: pytest tests/test_conversation.py::test_start_conversation -v -s
def test_start_conversation(authorized_client, test_user, test_conversations):
    user_messages = [
        "how are you doing?",
        "what is your name?",
        "who made you?",
        # "how do you say, hello how are you in Arabic?",
        # "what can you tell me about the Country named Mali?",
        # "what can you tell me about the Soninké people from Mali?",
    ]

    for user_message in user_messages:
        conversation_data = {
            "user_message": user_message,
            "llm_response": "",
            "conversations_summary": "",
            "created_at": ""
        }

        response = authorized_client.post("/conversation/start", json=conversation_data)

        # Assert that the response status code is 201 Created
        assert response.status_code == 201

        # Deserialize the response JSON
        response_data = response.json()

        # Assert the response structure and content
        assert response_data["user_message"] == conversation_data["user_message"]
        assert response_data["llm_response"] != ""  # Ensure llm_response is not empty
        assert response_data["conversations_summary"] != ""  # Ensure conversations_summary is not empty
        assert response_data["conversation_id"] != ""  # Ensure conversation_id is not empty
        # Retrieve created_at from the owner dictionary
        assert response_data["owner"]["created_at"] != ""  # Ensure created_at is not empty


# url: pytest tests/test_conversation.py::test_unauthorized_user_start_conversation -v -s
def test_unauthorized_user_start_conversation(client, test_user, test_conversations):
    response = client.post("/conversation/start", json={
        "user_message": "Good or Good ¡!¡",
        "llm_response": "string",
        "conversations_summary": "string"
        })
    assert response.status_code == 401


# url: pytest tests/test_conversation.py::test_user_update_conversation -v -s
def test_user_update_conversation(authorized_client, test_user, test_conversations): 
    conversation_data = {
        "user_message": "Good or Good ¡!¡",
        "llm_response": "string",
        "conversations_summary": "string"
        }
    response = authorized_client.put(f"/conversation/update/{test_conversations[0].id}", json=conversation_data)
    updated_conversation = schemas.MemoryCreate(**response.json())
    assert response.status_code == 200
    assert updated_conversation.user_message == conversation_data["user_message"]


# url: pytest tests/test_conversation.py::test_user_update_other_user_conversation -v -s
def test_user_update_other_user_conversation(authorized_client, test_user, test_conversations): 
    conversation_data = {
        "user_message": "Good or Good ¡!¡",
        "llm_response": "string",
        "conversations_summary": "string"
        }
    response = authorized_client.put(f"/conversation/update/{test_conversations[1].id}", json=conversation_data)
    assert response.status_code == 403


# url: pytest tests/test_conversation.py::test_unauthorized_user_update_conversation -v -s
def test_unauthorized_user_update_conversation(client, test_user, test_conversations):
    response = client.put(f"/conversation/update/{test_conversations[0].id}")
    assert response.status_code == 401


# url: pytest tests/test_conversation.py::test_user_update_conversation_not_found -v -s
def test_user_update_conversation_not_found(authorized_client, test_user, test_conversations):
    conversation_data = {
        "user_message": "Good or Good ¡!¡",
        "llm_response": "string",
        "conversations_summary": "string"
        }
    response = authorized_client.put(f"/conversation/update/991", json=conversation_data)
    assert response.status_code == 404


# url: pytest tests/test_conversation.py::test_unauthorized_user_delete_conversation -v -s
def test_unauthorized_user_delete_conversation(client, test_user, test_conversations):
    response = client.delete(f"/conversation/delete/{test_conversations[0].id}")
    assert response.status_code == 401


# url: pytest tests/test_conversation.py::test_user_delete_conversation_success -v -s
def test_user_delete_conversation_success(authorized_client, test_user, test_conversations):
    response = authorized_client.delete(f"/conversation/delete/{test_conversations[0].id}")
    assert response.status_code == 204


# url: pytest tests/test_conversation.py::test_user_delete_conversation_not_found -v -s
def test_user_delete_conversation_not_found(authorized_client, test_user, test_conversations):
    response = authorized_client.delete(f"/conversation/delete/991")
    assert response.status_code == 404


# url: pytest tests/test_conversation.py::test_user_delete_other_user_conversation -v -s
def test_user_delete_other_user_conversation(authorized_client, test_user, test_conversations):
    response = authorized_client.delete(f"/conversation/delete/{test_conversations[1].id}")
    assert response.status_code == 403
    