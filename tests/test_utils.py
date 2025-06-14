import os
import uuid
import pytest
import requests_mock
from app.utils import check_company_id, check_role_id, require_internal

def test_check_company_id_valid_uuid(monkeypatch):
    """
    Should return True for a valid UUID in testing environment.
    """
    monkeypatch.setenv("FLASK_ENV", "testing")
    assert check_company_id(str(uuid.uuid4())) is True

def test_check_company_id_invalid_uuid(monkeypatch):
    """
    Should raise ValueError for an invalid UUID.
    """
    monkeypatch.setenv("FLASK_ENV", "testing")
    with pytest.raises(ValueError):
        check_company_id("not-a-uuid")

def test_check_company_id_missing_env(monkeypatch):
    """
    Should raise ValueError if COMPANY_SERVICE_URL is not set in production.
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.delenv("COMPANY_SERVICE_URL", raising=False)
    with pytest.raises(ValueError):
        check_company_id(str(uuid.uuid4()))

def test_check_company_id_invalid_url(monkeypatch):
    """
    Should raise ValueError if COMPANY_SERVICE_URL is invalid.
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("COMPANY_SERVICE_URL", "ftp://badurl")
    with pytest.raises(ValueError):
        check_company_id(str(uuid.uuid4()))

def test_check_company_id_external_404(monkeypatch, requests_mock):
    """
    Should return False if the company is not found (404).
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("COMPANY_SERVICE_URL", "http://company")
    requests_mock.get("http://company/companies/123e4567-e89b-12d3-a456-426614174000", status_code=404)
    assert check_company_id("123e4567-e89b-12d3-a456-426614174000") is False

def test_check_company_id_external_200(monkeypatch, requests_mock):
    """
    Should return True if the company is found (200).
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("COMPANY_SERVICE_URL", "http://company")
    requests_mock.get("http://company/companies/123e4567-e89b-12d3-a456-426614174000", status_code=200)
    assert check_company_id("123e4567-e89b-12d3-a456-426614174000") is True

def test_check_role_id_valid(monkeypatch):
    """
    Should return True for a valid role ID in testing environment.
    """
    monkeypatch.setenv("FLASK_ENV", "testing")
    assert check_role_id(1) is True

def test_check_role_id_invalid(monkeypatch):
    """
    Should raise ValueError for a non-positive integer.
    """
    monkeypatch.setenv("FLASK_ENV", "testing")
    with pytest.raises(ValueError):
        check_role_id(0)
    with pytest.raises(ValueError):
        check_role_id("not-an-int")

def test_check_role_id_missing_env(monkeypatch):
    """
    Should raise ValueError if ROLE_SERVICE_URL is not set in production.
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.delenv("ROLE_SERVICE_URL", raising=False)
    with pytest.raises(ValueError):
        check_role_id(1)

def test_check_role_id_invalid_url(monkeypatch):
    """
    Should raise ValueError if ROLE_SERVICE_URL is invalid.
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("ROLE_SERVICE_URL", "ftp://badurl")
    with pytest.raises(ValueError):
        check_role_id(1)

def test_check_role_id_external_404(monkeypatch, requests_mock):
    """
    Should return False if the role is not found (404).
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("ROLE_SERVICE_URL", "http://role")
    requests_mock.get("http://role/roles/1", status_code=404)
    assert check_role_id(1) is False

def test_check_role_id_external_200(monkeypatch, requests_mock):
    """
    Should return True if the role is found (200).
    """
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("ROLE_SERVICE_URL", "http://role")
    requests_mock.get("http://role/roles/1", status_code=200)
    assert check_role_id(1) is True
