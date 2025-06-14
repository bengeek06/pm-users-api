import io
import json

def test_import_json_success(client):
    """
    Test importing valid JSON data via /import/json.
    """
    data = [
        {
            "email": "user1@example.com",
            "firstname": "User",
            "lastname": "One",
            "hashed_passwd": "x" * 60,
            "company_id": "123e4567-e89b-12d3-a456-426614174000",
            "role_id": 1,
            "is_active": True,
            "is_verified": False
        },
        {
            "email": "user2@example.com",
            "firstname": "User",
            "lastname": "Two",
            "hashed_passwd": "y" * 60,
            "company_id": "123e4567-e89b-12d3-a456-426614174000",
            "role_id": 1,
            "is_active": True,
            "is_verified": False
        }
    ]
    file_data = io.BytesIO(json.dumps(data).encode("utf-8"))
    file_data.seek(0)
    response = client.post(
        "/import/json",
        data={"file": (file_data, "users.json")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert b"records imported successfully" in response.data

def test_import_json_no_file(client):
    """
    Test importing with no file sent.
    """
    response = client.post("/import/json", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"No file part in the request" in response.data

def test_import_json_empty_file(client):
    """
    Test importing with an empty file field.
    """
    file_data = io.BytesIO(b"")
    response = client.post(
        "/import/json",
        data={"file": (file_data, "")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert b"No selected file" in response.data

def test_import_json_invalid_json(client):
    """
    Test importing with invalid JSON content.
    """
    file_data = io.BytesIO(b"not a json")
    response = client.post(
        "/import/json",
        data={"file": (file_data, "users.json")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert b"Invalid JSON" in response.data

def test_import_json_not_a_list(client):
    """
    Test importing with a JSON file that is not a list.
    """
    file_data = io.BytesIO(json.dumps({"email": "user@example.com"}).encode("utf-8"))
    response = client.post(
        "/import/json",
        data={"file": (file_data, "users.json")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert b"JSON must be a list of user objects" in response.data

def test_import_json_partial_success(client):
    """
    Test importing a list with one valid and one invalid item.
    """
    data = [
        {
            "email": "user1@example.com",
            "firstname": "User",
            "lastname": "One",
            "hashed_passwd": "x" * 60,
            "company_id": "123e4567-e89b-12d3-a456-426614174000",
            "role_id": 1,
            "is_active": True,
            "is_verified": False
        },
        {"firstname": "MissingEmail"}
    ]
    file_data = io.BytesIO(json.dumps(data).encode("utf-8"))
    response = client.post(
        "/import/json",
        data={"file": (file_data, "users.json")},
        content_type="multipart/form-data"
    )
    # 207 Multi-Status expected if at least one record is valid
    assert response.status_code == 207
    assert b"records imported" in response.data
    assert b"errors" in response.data

def test_import_csv_success(client):
    """
    Test importing valid CSV data via /import/csv.
    """
    csv_content = (
        "email,firstname,lastname,hashed_passwd,company_id,role_id,is_active,is_verified\n"
        "user1@example.com,User,One,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,123e4567-e89b-12d3-a456-426614174000,1,True,False\n"
        "user2@example.com,User,Two,yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy,123e4567-e89b-12d3-a456-426614174000,1,True,False\n"
    )
    file_data = io.BytesIO(csv_content.encode("utf-8"))
    response = client.post(
        "/import/csv",
        data={"file": (file_data, "users.csv")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert b"records imported successfully" in response.data

def test_import_csv_no_file(client):
    """
    Test importing with no file sent.
    """
    response = client.post("/import/csv", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"No file part in the request" in response.data

def test_import_csv_empty_file(client):
    """
    Test importing with an empty file field.
    """
    file_data = io.BytesIO(b"")
    response = client.post(
        "/import/csv",
        data={"file": (file_data, "")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert b"No selected file" in response.data

def test_import_csv_partial_success(client):
    """
    Test importing a CSV with one valid and one invalid row.
    """
    csv_content = (
        "email,firstname,lastname,hashed_passwd,company_id,role_id,is_active,is_verified\n"
        "user1@example.com,User,One,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,123e4567-e89b-12d3-a456-426614174000,1,True,False\n"
        ",User,NoEmail,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,123e4567-e89b-12d3-a456-426614174000,1,True,False\n"
    )
    file_data = io.BytesIO(csv_content.encode("utf-8"))
    response = client.post(
        "/import/csv",
        data={"file": (file_data, "users.csv")},
        content_type="multipart/form-data"
    )
    # Should return 207 Multi-Status if at least one row is valid
    assert response.status_code == 207
    assert b"records imported" in response.data
    assert b"errors" in response.data
