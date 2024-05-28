import pytest
from jose import jwt
from app import schemas
from app.config import settings


# url: pytest tests/test_users.py::test_root -v -s
def test_root(client):
    response = client.get('/')
    print(response.json())
    print(response.json().get(f'Be Good | Doing Good | By Acting Good\n'))
    assert response.json().get(f'Be Good | Doing Good | By Acting Good') == "Siisi-¡!¡-Chacal 🔥👌🏿😇💪🏿🔥"
    assert response.status_code == 200


# url: pytest tests/test_users.py::test_create_user -v -s
def test_create_user(client):
    response = client.post("/users/", json={"email": "dbt@dbt.com", "password": "dbt","name": "dbt"})
    print(f'new user created:\n{response.json()}\n')
    assert response.status_code == 201 

    new_user = schemas.UserOut(**response.json())
    print(f'new_user=(schemas.UserOut):\n{new_user}\ı')
    assert new_user.email == "dbt@dbt.com"


# url: pytest tests/test_users.py::test_login_user -v -s
def test_login_user(client, test_user):
    response = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    login_response = schemas.Token(**response.json())
    payload = jwt.decode(login_response.access_token, settings.admin_oauth2_secret_key, algorithms=settings.admin_algorithm)
    user_id = payload.get('user_id')
    assert user_id == test_user['id']
    assert login_response.token_type == 'bearer'
    assert response.status_code == 200


# url: pytest tests/test_users.py::test_incorrect_login -v -s
@pytest.mark.parametrize("email, password, status_code", [
                         ('wrongemail@gmail.com', 'dbt', 403),
                         ('dbt@dbt.com', 'wrongpassword', 403),
                         ('wrongemail@gmail.com', 'wrongpassword', 403),
                         ('dbt@dbt.com', 'dbt', 200),
                         (None, 'dbt', 422),
                         ('wrongemail@gmail.com', None, 422)
])
def test_incorrect_login(client, test_user, email, password, status_code):
    response = client.post("/login", 
                           data={"username": email,
                                 "password": password
    })
    assert response.status_code == status_code
    # assert response.json().get('detail') == 'Invalid Credentials 😝 ¡!¡'

