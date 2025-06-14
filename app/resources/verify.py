"""
verify.py
---------

This module defines the resource for verifying a user's password.
It provides an endpoint intended for internal authentication services to check
user credentials and return user information for JWT generation.

Classes:
    - UserVerifyPasswordResource: Resource for verifying user credentials via
        POST.
"""

from flask import request
from flask_restful import Resource
from werkzeug.security import check_password_hash
from app.models import User
from app.utils import require_internal
from app.logger import logger


class UserVerifyPasswordResource(Resource):
    """
    Resource for verifying a user's password and returning user info for JWT.
    Endpoint réservé au service d'authentification interne.
    """
    @require_internal
    def post(self):
        """
        Vérifie le mot de passe d'un utilisateur à partir de son email.

        Expects:
            {
                "email": "user@example.com",
                "password": "motdepasse"
            }

        Returns:
            Si succès :
                {
                    "valid": true,
                    "user_id": ...,
                    "company_id": ...,
                }
            Si échec :
                {
                    "valid": false
                }
        """
        logger.info("UserVerifyPasswordResource POST called")
        data = request.get_json()
        if not data or "email" not in data or "password" not in data:
            logger.error("Missing email or password in request data")
            return {"message": "Missing email or password"}, 400

        user = User.get_by_email(data["email"])
        if not user:
            logger.error("User with email %s not found", data["email"])
            return {"valid": False}, 404

        logger.info("Verifying password for user %s", user.email)
        if check_password_hash(user.hashed_passwd, data["password"]):
            return {
                "valid": True,
                "user_id": user.id,
                "company_id": user.company_id,
            }, 200
        return {"valid": False}, 401
