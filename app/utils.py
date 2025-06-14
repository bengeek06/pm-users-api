"""
utils.py
--------

Utility functions for validating company and role IDs.

Functions:
    - check_company_id(company_id): Validates that the given company ID is a
        valid UUID and exists in the external company service.
    - check_role_id(role_id): Validates that the given role ID is a positive
        integer and exists in the external role service.

These functions are used to ensure referential integrity between users and
external company/role services, and handle environment-specific logic for
development and testing.
"""
import os
import uuid
from functools import wraps
import requests
from flask import request, abort
from .logger import logger


def check_company_id(company_id):
    """
    Check if the company ID is valid.

    Args:
        company_id (str): The company ID (UUID) to check.

    Raises:
        ValueError: If the company ID is not a valid UUID string.
    """
    # Validate UUID format
    try:
        uuid.UUID(company_id)
    except (ValueError, TypeError) as exc:
        raise ValueError("Company ID must be a valid UUID string.") from exc

    env = os.getenv('FLASK_ENV')
    if env in ('development', 'testing'):
        logger.info("Skipping company ID check in %s environment", env)
        return True

    service = os.getenv("COMPANY_SERVICE_URL")
    if not service:
        logger.error("COMPANY_SERVICE_URL environment variable is not set.")
        raise ValueError(
            "COMPANY_SERVICE_URL environment variable is not set."
            )

    if not service.startswith("http://") and (
        not service.startswith("https://")
    ):
        logger.error("Invalid COMPANY_SERVICE_URL: %s", service)
        raise ValueError(
            "COMPANY_SERVICE_URL must start with 'http://' or 'https://'."
            )

    try:
        response = requests.get(f"{service}/companies/{company_id}", timeout=5)
        if response.status_code == 404:
            logger.error("Company ID %s not found", company_id)
            return False
        if response.status_code != 200:
            logger.error(
                "Unexpected status code %s for company ID %s",
                response.status_code, company_id
            )
            return False

        return True
    except requests.RequestException as e:
        logger.error("Error checking company ID %s: %s", company_id, e)
        raise ValueError(
            f"Failed to validate company ID {company_id}: {str(e)}"
            ) from e


def check_role_id(role_id):
    """
    Check if the role ID is valid.

    Args:
        role_id (int): The role ID to check.

    Raises:
        ValueError: If the role ID is not a positive integer or if the
            ROLE_SERVICE_URL environment variable is not set or invalid.

    Returns:
        bool: True if the role ID is valid, False if not found.
    """
    # Validate integer format
    if not isinstance(role_id, int) or role_id <= 0:
        raise ValueError("Role ID must be a positive integer.")

    env = os.getenv('FLASK_ENV')
    if env in ('development', 'testing'):
        logger.info("Skipping role ID check in %s environment", env)
        return True

    service = os.getenv("ROLE_SERVICE_URL")
    if not service:
        logger.error("ROLE_SERVICE_URL environment variable is not set.")
        raise ValueError("ROLE_SERVICE_URL environment variable is not set.")

    if not service.startswith("http://") and (
        not service.startswith("https://")
    ):
        logger.error("Invalid ROLE_SERVICE_URL: %s", service)
        raise ValueError(
            "ROLE_SERVICE_URL must start with 'http://' or 'https://'."
            )

    try:
        response = requests.get(f"{service}/roles/{role_id}", timeout=5)
        if response.status_code == 404:
            logger.error("Role ID %s not found", role_id)
            return False
        if response.status_code != 200:
            logger.error(
                "Unexpected status code %s for role ID %s",
                response.status_code, role_id
            )
            return False

        return True
    except requests.RequestException as e:
        logger.error("Error checking role ID %s: %s", role_id, e)
        raise ValueError(
            f"Failed to validate role ID {role_id}: {str(e)}"
        ) from e


def require_internal(f):
    """
    Decorator to ensure that the request is internal (from the same service).

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The wrapped function with internal request check.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        flask_env = os.environ.get('FLASK_ENV')
        logger.info("FLASK_ENV is set to: %s", flask_env)
        if not flask_env:
            logger.error(
                "FLASK_ENV is not set. Cannot validate internal request."
                )
            abort(500, description="Server configuration error")

        # Skip internal request check in test and development environments
        if flask_env in ('test', 'development'):
            logger.info(
             "Skipping internal request check in test/development env.")
            return f(*args, **kwargs)

        # Check for production or staging environments
        if flask_env in ('production', 'staging'):
            internal_token = os.environ.get('INTERNAL_REQUEST_SECRET')

            token = request.headers.get('X-Internal-Token')
            if not token:
                logger.error("Internal request token is missing.")
                abort(401, description="Internal request token is missing")
            if token != internal_token:
                logger.error("Invalid internal request token provided.")
                abort(401, description="Invalid internal request token")

        return f(*args, **kwargs)
    return decorated
