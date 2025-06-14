import json
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash
from app.models import User, db


# Tests for POST /users endpoint

def test_post_user_success(client):
    """
    Test creating a user with all required fields.
    """
    data = {
        "email": "user1@example.com",
        "password": "password",
        "firstname": "User",
        "lastname": "One",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 1,
        "is_active": True,
        "is_verified": False
    }
    response = client.post(
        "/users",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 201
    assert b"user1@example.com" in response.data

def test_post_user_missing_password(client):
    """
    Test creating a user without a password.
    """
    data = {
        "email": "user2@example.com",
        "firstname": "User",
        "lastname": "Two",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 1
    }
    response = client.post(
        "/users",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert b"Missing required field 'password'" in response.data

def test_post_user_validation_error(client):
    """
    Test creating a user with an invalid email.
    """
    data = {
        "email": "not-an-email",
        "password": "password",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 1
    }
    response = client.post(
        "/users",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert b"Validation error" in response.data

def test_post_user_duplicate_email(client):
    """
    Test creating a user with an already existing email.
    """
    # Création initiale
    User.create(
        email="user3@example.com",
        hashed_passwd="xxx",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1
    )
    data = {
        "email": "user3@example.com",
        "password": "password",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 1
    }
    response = client.post(
        "/users",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert b"Email must be unique." in response.data


def test_creater_integrity_error(client, monkeypatch):
    """
    Test POST /users with a mocked IntegrityError.
    This simulates a database integrity error during the creation process.
    """
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.session.commit", raise_integrity_error)

    data = { 'email': 'user1@example.com',
             'password': 'password',
             'firstname': 'Test',
             'lastname': 'Dummy',
             'company_id': "123e4567-e89b-12d3-a456-426614174000",
             'role_id': 1,
             'is_active': True,
             'is_verified': False
           }
    response = client.post("/users", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 400


def test_create_sqlalchemy_error(client, monkeypatch):
    """
    Test POST /users with a mocked SQLAlchemyError.
    This simulates a database error during the creation process.
    """
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    data = { 'email': 'user1@example.com',
             'password': 'password',
             'firstname': 'Test',
             'lastname': 'Dummy',
             'company_id': "123e4567-e89b-12d3-a456-426614174000",
             'role_id': 1,
             'is_active': True,
             'is_verified': False
           }
    response = client.post("/users", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 500



# Tests for GET /users endpoint

def test_get_users_empty(client):
    """
    Test GET /users quand il n'y a aucun utilisateur.
    """
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json == []

def test_get_users_one(client):
    """
    Test GET /users avec un utilisateur en base.
    """
    user = User.create(
        email="user1@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="User",
        lastname="One",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    response = client.get("/users")
    assert response.status_code == 200
    users = response.get_json()
    assert isinstance(users, list)
    assert any(u["email"] == "user1@example.com" for u in users)

def test_get_users_multiple(client):
    """
    Test GET /users avec plusieurs utilisateurs.
    """
    User.create(
        email="user2@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="User",
        lastname="Two",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    User.create(
        email="user3@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="User",
        lastname="Three",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    response = client.get("/users")
    assert response.status_code == 200
    users = response.get_json()
    emails = [u["email"] for u in users]
    assert "user2@example.com" in emails
    assert "user3@example.com" in emails

# Tests for PUT /users/<id> endpoint

def test_put_user_success(client):
    """
    Test updating a user with all required fields.
    """
    # Create a user to update
    user = User.create(
        email="user1@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="User",
        lastname="One",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    data = {
        "email": "user1@example.com",
        "firstname": "Updated",
        "lastname": "User",
        "password": "newpassword",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 2,
        "is_active": False,
        "is_verified": True
    }
    response = client.put(
        f"/users/{user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json["firstname"] == "Updated"
    assert response.json["role_id"] == 2
    assert response.json["is_active"] is False
    assert response.json["is_verified"] is True

def test_put_user_not_found(client):
    """
    Test updating a user that does not exist.
    """
    data = {
        "email": "nouser@example.com",
        "firstname": "No",
        "lastname": "User",
        "password": "password",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 1
    }
    response = client.put(
        "/users/unknownid",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 404
    assert b"User not found" in response.data

def test_put_user_validation_error(client):
    """
    Test updating a user with invalid data.
    """
    user = User.create(
        email="user2@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="User",
        lastname="Two",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1
    )
    data = {
        "email": "not-an-email",
        "firstname": "User",
        "lastname": "Two",
        "password": "password",
        "company_id": "123e4567-e89b-12d3-a456-426614174000",
        "role_id": 1
    }
    response = client.put(
        f"/users/{user.id}",
        data=json.dumps(data),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert b"Validation error" in response.data


def test_update_integrity_error(client, monkeypatch):
    """
    Test PUT /users/<id> with a mocked IntegrityError.
    This simulates a database integrity error during the update process.
    """
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)

    # First, create a dummy object to update
    user = User.create(
        email='user1@example.com',
        hashed_passwd=generate_password_hash('password'),
        firstname='Test',
        lastname='Dummy',
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.session.commit", raise_integrity_error)

    data = { 'email': 'user1@example.com',
             'password': 'password',
             'firstname': 'foo',
             'lastname': 'bar',
             'company_id': "123e4567-e89b-12d3-a456-426614174000",
             'role_id': 1,
             'is_active': True,
             'is_verified': False
           }
    response = client.put(
        f"/users/{user.id}",
        data=json.dumps(data),
        content_type="application/json"
        )
    assert response.status_code == 400


def test_update_sqlalchemy_error(client, monkeypatch):
    """
    Test PUT /dummies/<id> with a mocked SQLAlchemyError.
    This simulates a database error during the update process.
    """
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    # First, create a dummy object to update
    user = User.create(
        email='user1@example.com',
        hashed_passwd=generate_password_hash('password'),
        firstname='Test',
        lastname='Dummy',
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )

    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    data = { 'email': 'user1@example.com',
             'password': 'password',
             'firstname': 'foo',
             'lastname': 'bar',
             'company_id': "123e4567-e89b-12d3-a456-426614174000",
             'role_id': 1,
             'is_active': True,
             'is_verified': False
           }
    response = client.put(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 500

# Tests for PATCH /dummies/<id> endpoint

def test_patch_user_success(client):
    """
    Test partially updating a user with valid fields.
    """
    # Create a user to update
    user = User.create(
        email="patchuser@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="Patch",
        lastname="User",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    patch_data = {
        "firstname": "Patched",
        "is_active": False
    }
    response = client.patch(
        f"/users/{user.id}",
        data=json.dumps(patch_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json["firstname"] == "Patched"
    assert response.json["is_active"] is False

def test_patch_user_password(client):
    """
    Test partially updating a user's password.
    """
    user = User.create(
        email="patchpass@example.com",
        hashed_passwd=generate_password_hash("oldpassword"),
        firstname="Patch",
        lastname="Pass",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1
    )
    patch_data = {
        "password": "newpassword"
    }
    response = client.patch(
        f"/users/{user.id}",
        data=json.dumps(patch_data),
        content_type="application/json"
    )
    assert response.status_code == 200
    # Optionally, check that the password was actually changed (hash differs)
    assert response.json["email"] == "patchpass@example.com"

def test_patch_user_not_found(client):
    """
    Test patching a user that does not exist.
    """
    patch_data = {
        "firstname": "Ghost"
    }
    response = client.patch(
        "/users/unknownid",
        data=json.dumps(patch_data),
        content_type="application/json"
    )
    assert response.status_code == 404
    assert b"User not found" in response.data

def test_patch_user_validation_error(client):
    """
    Test patching a user with invalid data.
    """
    user = User.create(
        email="patchval@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="Patch",
        lastname="Val",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1
    )
    patch_data = {
        "email": "not-an-email"
    }
    response = client.patch(
        f"/users/{user.id}",
        data=json.dumps(patch_data),
        content_type="application/json"
    )
    assert response.status_code == 400
    assert b"Validation error" in response.data

def test_partial_update_integrity_error(client, monkeypatch):
    """
    Test PATCH /users/<id> with a mocked IntegrityError.
    This simulates a database integrity error during the update process.
    """
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)

    # First, create a user object to update
    user = User.create(
        email='user1@example.com',
        hashed_passwd=generate_password_hash('password'),
        firstname='Test',
        lastname='Dummy',
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.session.commit", raise_integrity_error)

    response = client.patch(f'/users/{user.id}', json={'email': 'updated@example.com'})
    assert response.status_code == 400


def test_partial_update_sqlalchemy_error(client, monkeypatch):
    """
    Test PATCH /users/<id> with a mocked SQLAlchemyError.
    This simulates a database error during the update process.
    """
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    user = User.create(
        email='user1@example.com',
        hashed_passwd=generate_password_hash('password'),
        firstname='Test',
        lastname='Dummy',
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )

    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    response = client.patch(f'/users/{user.id}', json={'email': 'updated@example.com'})
    assert response.status_code == 500

def test_user_schema_patch_fields(client):
    """
    Test PATCH /users/<id> with valid and invalid values for each UserSchema field.
    """
    # Crée un utilisateur de base
    user = User.create(
        email="schemauser@example.com",
        hashed_passwd=generate_password_hash("password"),
        firstname="Schema",
        lastname="User",
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    user_id = user.id

    # Champs à tester : {champ: (valide, invalide)}
    fields = {
        "email": ("ok@example.com", "not-an-email"),
        "firstname": ("John", "J"*81),
        "lastname": ("Doe", "D"*81),
        "phone_number": ("0123456789", "1"*21),
        "avatar_url": ("http://img.com/a.png", "a"*257),
        "is_active": (True, "notabool"),
        "is_verified": (False, "notabool"),
        "language": ("en", "x"*11),
        "company_id": ("123e4567-e89b-12d3-a456-426614174000", "not-a-uuid"),
        "role_id": (1, -1),
        "hashed_passwd": (generate_password_hash("newpass"), ""),  # direct hash
        "last_login_at": ("2023-01-01T12:00:00", "not-a-date"),
    }

    for field, (good, bad) in fields.items():
        # PATCH avec valeur valide
        resp = client.patch(
            f"/users/{user_id}",
            data=json.dumps({field: good}),
            content_type="application/json"
        )
        assert resp.status_code == 200, f"{field} valid value should pass"

        # PATCH avec valeur invalide
        resp = client.patch(
            f"/users/{user_id}",
            data=json.dumps({field: bad}),
            content_type="application/json"
        )
        assert resp.status_code == 400, f"{field} invalid value should fail"
        assert b"Validation error" in resp.data

def test_patch_firstname_too_long(client, user):
    data = {"firstname": "A" * 81}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 80." in resp.data

def test_patch_lastname_too_long(client, user):
    data = {"lastname": "B" * 81}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 80." in resp.data

def test_patch_phone_number_too_long(client, user):
    data = {"phone_number": "1" * 21}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 20." in resp.data

def test_patch_avatar_url_too_long(client, user):
    data = {"avatar_url": "h" * 257}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 256." in resp.data

def test_patch_language_too_long(client, user):
    data = {"language": "l" * 11}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 10." in resp.data

def test_patch_email_too_long(client, user):
    data = {"email": ("a" * 120) + "@ex.com"}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 120." in resp.data

def test_patch_hashed_passwd_too_long(client, user):
    data = {"hashed_passwd": "x" * 257}
    resp = client.patch(f"/users/{user.id}", data=json.dumps(data), content_type="application/json")
    assert resp.status_code == 400
    assert b"Longer than maximum length 256." in resp.data

# Tests for DELETE /dummies/<id> endpoint

def test_delete_user_success(client):
    """
    Test DELETE /users/<id> should delete the user.
    """
    data = { 'email': 'user1@example.com',
             'password': 'password',
             'firstname': 'Test',
             'lastname': 'Dummy',
             'company_id': "123e4567-e89b-12d3-a456-426614174000",
             'role_id': 1,
             'is_active': True,
             'is_verified': False
           }
    post_resp = client.post("/users", data=json.dumps(data), content_type="application/json")
    user_id = post_resp.json["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    # Should not be found anymore
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404

def test_delete_users_not_found(client):
    """
    Test DELETE /users/<id> with an unknown id should return 404.
    """
    response = client.delete("/users/unknown-id")
    assert response.status_code == 404
    assert response.json["message"] == "User not found"

def test_delete_sqlalchemy_error(client, monkeypatch):
    """
    Test DELETE /users/<id> with a mocked SQLAlchemyError.
    This simulates a database error during the deletion process.
    """
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    # First, create a user object to delete (avec tous les champs obligatoires)
    user = User.create(
        email='user1@example.com',
        hashed_passwd=generate_password_hash('password'),
        firstname='Test',
        lastname='Dummy',
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )

    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    response = client.delete(f'/users/{user.id}')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'message' in data
    assert 'error' in data
    assert data['message'] == 'Database error'



def test_model_repr(app):
    """
    Test the __repr__ method of the User model.
    """
    _= app.app_context()

    user = User.create(
        email='user1@example.com',
        hashed_passwd=generate_password_hash('password'),
        firstname='Test',
        lastname='Dummy',
        company_id="123e4567-e89b-12d3-a456-426614174000",
        role_id=1,
        is_active=True,
        is_verified=False
    )
    expected_repr = (
    f"<User {user.email}> (ID: {user.id}, Email: {user.email}, First Name: {user.firstname}, "
    f"Last Name: {user.lastname}, Phone: {user.phone_number}, Active: {user.is_active}, "
    f"Verified: {user.is_verified}, Language: {user.language}, Company ID: {user.company_id}, "
    f"Role ID: {user.role_id}, Last Login: {user.last_login_at}, "
    f"Created At: {user.created_at}, Updated At: {user.updated_at})"
    )
    assert repr(user) == expected_repr, f"Expected: {expected_repr}, got: {repr(user)}"
