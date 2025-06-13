import json
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import Dummy, db

# Tests for POST /dummies endpoint

def test_create_dummy(client):
    """
    Test the creation of a Dummy object via the API.
    """
    response = client.post('/dummies', json={'name': 'Test Dummy'})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test Dummy'
    assert 'id' in data


def test_create_dummy_validation_error(client):
    """
    Test validation error when creating a Dummy object with missing fields.
    """
    response = client.post('/dummies', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'errors' in data
    assert 'name' in data['errors']

def test_create_missing_name(client):
    """
    Test creating a Dummy object with a missing name field.
    """
    response = client.post('/dummies', json={'description': 'A test dummy without a name'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'errors' in data
    assert 'name' in data['errors']

def test_create_duplicate_name(client):
    """
    Test creating a Dummy object with a duplicate name.
    """
    # First, create a dummy object
    client.post('/dummies', json={'name': 'Duplicate Dummy'})

    # Attempt to create another dummy with the same name
    response = client.post('/dummies', json={'name': 'Duplicate Dummy'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'errors' in data
    assert 'name' in data['errors']

def test_create_long_description(client):
    """
    Test creating a Dummy object with a description that exceeds the maximum length.
    """
    long_description = 'A' * 201  # 201 characters long
    response = client.post('/dummies', json={'name': 'Test Dummy', 'description': long_description})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'errors' in data
    assert 'description' in data['errors']


def test_creater_integrity_error(client, monkeypatch):
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.session.commit", raise_integrity_error)

    response = client.post('/dummies', json={'name': 'Test Dummy'})
    assert response.status_code == 400


def test_create_sqlalchemy_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    response = client.post('/dummies', json={'name': 'Test Dummy'})
    assert response.status_code == 500



# Tests for GET /dummies endpoint

def test_get_all_dummies(client):
    """
    Test retrieving all Dummy objects via the API.
    """
    # First, create a dummy object to retrieve
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.get('/dummies')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['id'] == dummy.id
    assert data[0]['name'] == 'Test Dummy'
    assert data[0]['description'] == 'A test dummy'

# Tests for GET /dummies/<id> endpoint

def test_get_dummy_by_id(client):
    """
    Test retrieving a Dummy object by its ID via the API.
    """
    # First, create a dummy object to retrieve
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.get(f'/dummies/{dummy.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == dummy.id
    assert data['name'] == 'Test Dummy'
    assert data['description'] == 'A test dummy'


def test_get_dummy_by_id_not_found(client):
    """
    Test retrieving a Dummy object by ID that does not exist.
    """
    response = client.get('/dummies/9999')  # Assuming 9999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Dummy not found'

# Tests for PUT /dummies/<id> endpoint


def test_update_dummy(client):
    """
    Test updating a Dummy object via the API.
    """
    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.put(f'/dummies/{dummy.id}', json={'name': 'Updated Dummy'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == dummy.id
    assert data['name'] == 'Updated Dummy'
    
    
def test_update_dummy_not_found(client):
    """
    Test updating a Dummy object that does not exist.
    """
    response = client.put('/dummies/9999', json={'name': 'Updated Dummy'})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Dummy not found'
    
    
def test_update_dummy_validation_error(client):
    """
    Test validation error when updating a Dummy object with invalid data.
    """
    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.put(f'/dummies/{dummy.id}', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'errors' in data
    assert 'name' in data['errors']

def test_update_integrity_error(client, monkeypatch):
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)
    
    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.session.commit", raise_integrity_error)

    response = client.put('/dummies/1', json={'name': 'Updated Dummy'})
    assert response.status_code == 400


def test_update_sqlalchemy_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()
    
    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    response = client.put('/dummies/1', json={'name': 'Updated Dummy'})
    assert response.status_code == 500

# Tests for PATCH /dummies/<id> endpoint

def test_partial_update_dummy(client):
    """
    Test partially updating a Dummy object via the API.
    """
    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.patch(f'/dummies/{dummy.id}', json={'description': 'Updated description'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == dummy.id
    assert data['name'] == 'Test Dummy'
    assert data['description'] == 'Updated description'

def test_partial_update_dummy_not_found(client):
    """
    Test partially updating a Dummy object that does not exist.
    """
    response = client.patch('/dummies/9999', json={'description': 'Updated description'})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Dummy item not found'

def test_partial_update_dummy_validation_error(client):
    """
    Test validation error when partially updating a Dummy object with invalid data.
    """
    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.patch(f'/dummies/{dummy.id}', json={"invalid_field": "Invalid value"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data
    assert 'errors' in data

def test_partial_update_integrity_error(client, monkeypatch):
    # Fonction qui lève l'exception
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError("Mocked IntegrityError", None, None)
    
    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    # Monkeypatch la méthode commit
    monkeypatch.setattr("app.models.db.session.commit", raise_integrity_error)

    response = client.patch('/dummies/1', json={'name': 'Updated Dummy'})
    assert response.status_code == 400


def test_partial_update_sqlalchemy_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    # First, create a dummy object to update
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()
    
    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    response = client.patch('/dummies/1', json={'name': 'Updated Dummy'})
    assert response.status_code == 500


# Tests for DELETE /dummies/<id> endpoint

def test_delete_dummy(client):
    """
    Test deleting a Dummy object via the API.
    """
    # First, create a dummy object to delete
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()

    response = client.delete(f'/dummies/{dummy.id}')
    assert response.status_code == 204  # No content on successful deletion

    # Verify that the dummy is deleted
    response = client.get(f'/dummies/{dummy.id}')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Dummy not found'

def test_delete_dummy_not_found(client):
    """
    Test deleting a Dummy object that does not exist.
    """
    response = client.delete('/dummies/9999')  # Assuming 9999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Dummy not found'

def test_delete_sqlalchemy_error(client, monkeypatch):
    def raise_sqlalchemy_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemyError")

    # First, create a dummy object to delete
    dummy = Dummy.create(name='Test Dummy', description='A test dummy')
    db.session.commit()
    
    monkeypatch.setattr("app.models.db.session.commit", raise_sqlalchemy_error)

    response = client.delete(f'/dummies/{dummy.id}')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'message' in data
    assert 'error' in data
    assert data['message'] == 'Database error'



def test_model_repr():
    """
    Test the __repr__ method of the Dummy model.
    """
    dummy = Dummy(name='Test Dummy', description='A test dummy')
    expected_repr = f"<Dummy {dummy.name}> (ID: {dummy.id}, Description: {dummy.description})"
    assert repr(dummy) == expected_repr
