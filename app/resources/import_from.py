"""
import.py
---------

This module defines resources for importing data into the application
from CSV and JSON files via REST endpoints.
"""
import csv
import json
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, db
from app.schemas import UserSchema
from app.logger import logger


class ImportJSONResource(Resource):
    """
    Resource for importing users from a JSON file generated by GET /users.

    Methods:
        post():
            Import users from a JSON file and return a success message.
    """

    def post(self):
        """
        Import users from a JSON file uploaded via multipart/form-data.

        Expects:
            A file field named 'file' containing a JSON array of user objects,
            as returned by GET /users.

        Returns:
            dict: A success message indicating the number of records imported,
            or an error message.
        """
        if 'file' not in request.files:
            logger.error("No file part in the request.")
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file.")
            return {"message": "No selected file."}, 400

        try:
            data = json.load(file)
            if not isinstance(data, list):
                logger.error("JSON must be a list of user objects.")
                return {"message": "JSON must be a list of user objects."}, 400

            count = 0
            errors = []
            for idx, item in enumerate(data):
                # Convert empty strings to None
                for key, value in item.items():
                    if value == '':
                        item[key] = None
                try:
                    schema = UserSchema(session=db.session)
                    schema.context = {}
                    validated = schema.load(item)
                    # validated est un objet User (pas un dict)
                    user = None
                    if getattr(validated, "id", None):
                        user = User.get_by_id(validated.id)
                    if not user and getattr(validated, "email", None):
                        user = User.get_by_email(validated.email)
                    if user:
                        # On update avec les données du dict d'origine (item)
                        user.update(**item)
                    else:
                        User.create(**item)
                    count += 1
                except ValidationError as e:
                    logger.error(
                        "Validation error at index %s: %s",
                        idx,
                        e.messages
                        )
                    errors.append({"index": idx, "error": e.messages})
                except Exception as e:
                    logger.error(
                        "Unexpected error at index %s: %s",
                        idx,
                        str(e)
                        )
                    errors.append({"index": idx, "error": str(e)})

            if errors:
                logger.warning(
                    "%s errors encountered during import.",
                    len(errors)
                    )
                return {
                  "message": f"{count} records imported, {len(errors)} errors",
                  "errors": errors
                }, 400 if count == 0 else 207  # 207: Multi-Status

            return {"message": f"{count} records imported successfully."}, 200
        except (json.JSONDecodeError, TypeError) as e:
            logger.error("JSON parsing error: %s", str(e))
            return {"message": f"Invalid JSON file: {str(e)}"}, 400
        except SQLAlchemyError as e:
            logger.error("Database error: %s", str(e))
            db.session.rollback()
            return {"message": f"Database error: {str(e)}"}, 400


class ImportCSVResource(Resource):
    """
    Resource for importing users from a CSV file generated by
    ExportCSVResource.

    Methods:
        post():
            Import users from a CSV file and return a success message.
    """

    def post(self):
        """
        Import users from a CSV file uploaded via multipart/form-data.

        Expects:
            A file field named 'file' containing a CSV file with columns
            matching the User export (id, email, firstname, lastname,
            phone_number, avatar_url, is_active, is_verified, language,
            company_id, role_id, last_login_at, created_at, updated_at).

        Returns:
            dict: A success message indicating the number of records imported,
            or an error message.
        """
        if 'file' not in request.files:
            logger.error("No file part in the request.")
            return {"message": "No file part in the request."}, 400

        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file.")
            return {"message": "No selected file."}, 400

        try:
            # Read CSV file
            stream = file.stream.read().decode('utf-8').splitlines()
            reader = csv.DictReader(stream)
            count = 0
            errors = []
            for idx, row in enumerate(reader):
                # Convert string booleans to bool
                for bool_field in ["is_active", "is_verified"]:
                    if bool_field in row:
                        val = row[bool_field]
                        if isinstance(val, str):
                            row[bool_field] = (
                                val.lower() in ("true", "1", "yes")
                            )
                # Convert empty strings to None
                for key, value in row.items():
                    if value == '':
                        row[key] = None
                try:
                    schema = UserSchema(session=db.session)
                    schema.context = {}
                    validated = schema.load(row)
                    # validated est un objet User (pas un dict)
                    user = None
                    if getattr(validated, "id", None):
                        user = User.get_by_id(validated.id)
                    if not user and getattr(validated, "email", None):
                        user = User.get_by_email(validated.email)
                    if user:
                        user.update(**row)
                    else:
                        User.create(**row)
                    count += 1
                except ValidationError as e:
                    logger.error(
                        "Validation error at row %s: %s",
                        idx,
                        e.messages
                        )
                    errors.append({"index": idx, "error": e.messages})
                except Exception as e:
                    logger.error("Unexpected error at row %s: %s", idx, str(e))
                    errors.append({"index": idx, "error": str(e)})

            if errors:
                logger.warning(
                    "%s errors encountered during import.",
                    len(errors)
                    )
                return {
                  "message": f"{count} records imported, {len(errors)} errors",
                  "errors": errors
                }, 400 if count == 0 else 207  # 207: Multi-Status

            return {"message": f"{count} records imported successfully."}, 200
        except (csv.Error, UnicodeDecodeError) as e:
            logger.error("CSV parsing error: %s", str(e))
            return {"message": f"Invalid CSV file: {str(e)}"}, 400
        except SQLAlchemyError as e:
            logger.error("Database error: %s", str(e))
            db.session.rollback()
            return {"message": f"Database error: {str(e)}"}, 400
