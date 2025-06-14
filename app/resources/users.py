"""
resources.py
-----------
This module defines the resources for managing dummy items in the application.
It includes endpoints for creating, retrieving, updating, and deleting dummy.
"""
from flask import request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Resource
from werkzeug.security import generate_password_hash

from app.models import db, User
from app.schemas import UserSchema
from app.logger import logger


class UserListResource(Resource):
    """
    Resource for managing the collection of dummy items.

    Methods:
        get():
            Retrieve all dummy items from the database.

        post():
            Create a new dummy item with the provided data.
    """

    def get(self):
        """
        Retrieve all dummy items.

        Returns:
            tuple: A tuple containing a list of serialized dummy items and the
            HTTP status code 200.
        """
        logger.info("Retrieving all users")

        user = User.get_all()
        user_schemas = UserSchema(session=db.session, many=True)

        return user_schemas.dump(user), 200

    def post(self):
        """
        Create a new user.

        Expects:
            JSON payload with at least the 'email' and 'passwd' fields.
            Optionally, an 'id' field for import/export compatibility.

        Returns:
            tuple: The serialized created user and HTTP status code 201 on
                success.
            tuple: Error message and HTTP status code 400 ou 500 on failure.
        """
        logger.info("Creating a new user")

        json_data = request.get_json()
        marshmallow_data = dict(json_data)
        password = marshmallow_data.pop("password", None)
        if not password:
            logger.error("Missing required field 'password'")
            return {"message": "Missing required field 'password'"}, 400

        marshmallow_data["hashed_passwd"] = generate_password_hash(password)

        user_schema = UserSchema(session=db.session)
        user_schema.context = {}

        try:
            user_schema.load(marshmallow_data)
        except ValidationError as err:
            logger.error("Validation error: %s", err.messages)
            return {"message": "Validation error", "errors": err.messages}, 400

        try:
            user = User.create(**marshmallow_data)
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Integrity error: %s", str(e))
            return {"message": "Integrity error", "error": str(e)}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error: %s", str(e))
            return {"message": "Database error", "error": str(e)}, 500

        return user_schema.dump(user), 201


class UserResource(Resource):
    """
    Resource for managing a single dummy item by its ID.

    Methods:
        get(dummy_id):
            Retrieve a dummy item by its ID.

        put(dummy_id):
            Update a dummy item by replacing all fields.

        patch(dummy_id):
            Partially update a dummy item.

        delete(dummy_id):
            Delete a dummy item by its ID.
    """

    def get(self, user_id):
        """
        Retrieve a dummy item by its ID.

        Args:
            dummy_id (int): The ID of the dummy item to retrieve.

        Returns:
            tuple: The serialized dummy item and HTTP status code 200 if found.
            tuple: Error message and HTTP status code 404 if not found.
        """
        logger.info("Retrieving user with ID: %s", user_id)

        user = User.get_by_id(user_id)
        if not user:
            logger.warning("User with ID %s not found", user_id)
            return {"message": "User not found"}, 404

        user_schema = UserSchema(session=db.session)
        user_schema.context = {}  # Correction : toujours définir le context

        return user_schema.dump(user), 200

    def put(self, user_id):
        """
        Update a user by replacing all fields.

        Args:
            user_id (str): The ID of the user to update.

        Expects:
            JSON payload with the new user fields.

        Returns:
            tuple: The serialized updated user and HTTP status code 200 on
                    success.
            tuple: Error message and HTTP status code 400, 404, or 500 on
                    failure.
        """
        logger.info("Updating user with ID: %s", user_id)

        user = User.get_by_id(user_id)
        if not user:
            logger.warning("User with ID %s not found", user_id)
            return {"message": "User not found"}, 404

        user_schema = UserSchema(session=db.session)
        user_schema.context = {'user_id': user.id}
        json_data = request.get_json()
        marshmallow_data = dict(json_data)
        password = marshmallow_data.pop("password", None)
        if password:
            marshmallow_data["hashed_passwd"] = (
                generate_password_hash(password)
            )

        try:
            user_schema.load(marshmallow_data)
        except ValidationError as err:
            logger.error("Validation error: %s", err.messages)
            return {"message": "Validation error", "errors": err.messages}, 400

        try:
            update_kwargs = {
                "email": marshmallow_data.get("email"),
                "firstname": marshmallow_data.get("firstname"),
                "lastname": marshmallow_data.get("lastname"),
                "phone_number": marshmallow_data.get("phone_number"),
                "avatar_url": marshmallow_data.get("avatar_url"),
                "is_active": marshmallow_data.get("is_active"),
                "is_verified": marshmallow_data.get("is_verified"),
                "language": marshmallow_data.get("language"),
                "company_id": marshmallow_data.get("company_id"),
                "role_id": marshmallow_data.get("role_id"),
            }
            if "hashed_passwd" in marshmallow_data:
                update_kwargs["hashed_passwd"] = (
                    marshmallow_data["hashed_passwd"]
                )
            user.update(
                **{k: v for k, v in update_kwargs.items() if v is not None}
                )
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Integrity error: %s", str(e))
            return {"message": "Integrity error", "error": str(e)}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error: %s", str(e))
            return {"message": "Database error", "error": str(e)}, 500

        return user_schema.dump(user), 200

    def patch(self, user_id):
        """
        Partially update a user.

        Args:
            user_id (str): The ID of the user to update.

        Expects:
            JSON payload with fields to update.

        Returns:
            tuple: The serialized updated user and HTTP status code 200 on
                success.
            tuple: Error message and HTTP status code 400, 404, or 500 on
                failure.
        """
        logger.info("Partially updating user with ID: %s", user_id)

        user = User.get_by_id(user_id)
        if not user:
            logger.warning("User with ID %s not found", user_id)
            return {"message": "User not found"}, 404

        json_data = request.get_json()
        marshmallow_data = dict(json_data)
        password = marshmallow_data.pop("password", None)
        if password:
            marshmallow_data["hashed_passwd"] = (
                generate_password_hash(password)
            )

        user_schema = UserSchema(session=db.session)
        user_schema.context = {'user_id': user.id}
        try:
            user_schema.load(marshmallow_data, partial=True)
        except ValidationError as err:
            logger.error("Validation error: %s", err.messages)
            return {"message": "Validation error", "errors": err.messages}, 400

        update_kwargs = {
            "email": marshmallow_data.get("email"),
            "firstname": marshmallow_data.get("firstname"),
            "lastname": marshmallow_data.get("lastname"),
            "phone_number": marshmallow_data.get("phone_number"),
            "avatar_url": marshmallow_data.get("avatar_url"),
            "is_active": marshmallow_data.get("is_active"),
            "is_verified": marshmallow_data.get("is_verified"),
            "language": marshmallow_data.get("language"),
            "company_id": marshmallow_data.get("company_id"),
            "role_id": marshmallow_data.get("role_id"),
        }
        if "hashed_passwd" in marshmallow_data:
            update_kwargs["hashed_passwd"] = marshmallow_data["hashed_passwd"]

        try:
            user.update(
                **{k: v for k, v in update_kwargs.items() if v is not None}
                )
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Integrity error: %s", str(e))
            return {"message": "Integrity error", "error": str(e)}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error: %s", str(e))
            return {"message": "Database error", "error": str(e)}, 500

        return user_schema.dump(user), 200

    def delete(self, user_id):
        """
        Delete a user by its ID.

        Args:
            user_id (str): The ID of the user to delete.

        Returns:
            tuple: Success message and HTTP status code 204 if deleted.
            tuple: Error message and HTTP status code 404 or 500 on failure.
        """
        logger.info("Deleting user with ID: %s", user_id)

        user = User.get_by_id(user_id)
        if not user:
            logger.warning("User with ID %s not found", user_id)
            return {"message": "User not found"}, 404

        try:
            user.delete()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error: %s", str(e))
            return {"message": "Database error", "error": str(e)}, 500

        return {"message": "User deleted successfully"}, 204
