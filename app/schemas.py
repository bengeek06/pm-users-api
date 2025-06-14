"""
schemas.py
----------

This module defines Marshmallow schemas for serializing and validating
the application's data models.

Classes:
    - UserSchema: Schema for serializing and validating User model instances.
"""
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import ValidationError, validates, fields

from .models import User
from .utils import check_company_id, check_role_id


class UserSchema(SQLAlchemyAutoSchema):
    """
    Serialization and validation schema for the User model.

    Attributes:
        id (str): Unique identifier for the User entity.
        email (str): Email address of the User.
        hashed_passwd (str): Hashed password of the User.
        firstname (str): First name of the User.
        lastname (str): Last name of the User.
        phone_number (str): Phone number of the User.
        avatar_url (str): Avatar URL of the User.
        is_active (bool): Whether the User is active.
        is_verified (bool): Whether the User is verified.
        language (str): Preferred language of the User.
        company_id (int): Company ID associated with the User.
        role_id (int): Role ID associated with the User.
        last_login_at (datetime): Last login datetime.
        created_at (datetime): Creation datetime.
        updated_at (datetime): Last update datetime.
    """
    class Meta:
        """
        Meta options for the User schema.

        Attributes:
            model: The SQLAlchemy model associated with this schema.
            load_instance: Whether to load model instances.
            include_fk: Whether to include foreign keys.
            dump_only: Fields that are only used for serialization.
            load_only: Fields that are only used for deserialization.
        """
        model = User
        load_instance = True
        include_fk = True
        dump_only = ('id', 'created_at', 'updated_at')
        load_only = ('hashed_passwd',)
        last_login_at = fields.DateTime(allow_none=True)

    @validates('email')
    def validate_email(self, value, **kwargs):
        """
        Validate that the email is not empty, unique, and properly formatted.

        Args:
            value (str): The email to validate.

        Raises:
            ValidationError: If the email is empty, already exists, is not
              ASCII, does not contain '@', is too long, or is only whitespace.

        Returns:
            str: The validated email.
        """
        _ = kwargs

        if not value:
            raise ValidationError("Email cannot be empty.")
        # Get current user id from schema context if present
        current_user_id = self.context.get('user_id')
        email_user = User.query.filter_by(email=value).first()
        if email_user and (
           not current_user_id or email_user.id != current_user_id
           ):
            raise ValidationError("Email must be unique.")
        if '@' not in value:
            raise ValidationError("Email must contain '@' character.")
        if len(value) > 120:
            raise ValidationError("Email cannot exceed 120 characters.")
        if not value.strip():
            raise ValidationError("Email cannot be just whitespace.")
        if not value.isascii():
            raise ValidationError("Email must be ASCII characters only.")
        return value

    @validates('firstname')
    def validate_firstname(self, value, **kwargs):
        """
        Validate that the first name does not exceed 80 characters.

        Args:
            value (str): The first name to validate.

        Raises:
            ValidationError: If the first name exceeds 80 characters.

        Returns:
            str: The validated first name.
        """
        _ = kwargs
        if value and len(value) > 80:
            raise ValidationError("First name cannot exceed 80 characters.")
        return value

    @validates('lastname')
    def validate_lastname(self, value, **kwargs):
        """
        Validate that the last name does not exceed 80 characters.

        Args:
            value (str): The last name to validate.

        Raises:
            ValidationError: If the last name exceeds 80 characters.

        Returns:
            str: The validated last name.
        """
        _ = kwargs
        if value and len(value) > 80:
            raise ValidationError("Last name cannot exceed 80 characters.")
        return value

    @validates('phone_number')
    def validate_phone_number(self, value, **kwargs):
        """
        Validate that the phone number does not exceed 20 characters.

        Args:
            value (str): The phone number to validate.

        Raises:
            ValidationError: If the phone number exceeds 20 characters.

        Returns:
            str: The validated phone number.
        """
        _ = kwargs
        if value and len(value) > 20:
            raise ValidationError("Phone number cannot exceed 20 characters.")
        return value

    @validates('avatar_url')
    def validate_avatar_url(self, value, **kwargs):
        """
        Validate that the avatar URL does not exceed 256 characters.

        Args:
            value (str): The avatar URL to validate.

        Raises:
            ValidationError: If the avatar URL exceeds 256 characters.

        Returns:
            str: The validated avatar URL.
        """
        _ = kwargs
        if value and len(value) > 256:
            raise ValidationError("Avatar URL cannot exceed 256 characters.")
        return value

    @validates('is_active')
    def validate_is_active(self, value, **kwargs):
        """
        Validate that the is_active field is a boolean.

        Args:
            value (bool): The is_active value to validate.

        Raises:
            ValidationError: If the value is not a boolean.

        Returns:
            bool: The validated is_active value.
        """
        _ = kwargs
        if not isinstance(value, bool):
            raise ValidationError("is_active must be a boolean.")
        return value

    @validates('is_verified')
    def validate_is_verified(self, value, **kwargs):
        """
        Validate that the is_verified field is a boolean.

        Args:
            value (bool): The is_verified value to validate.

        Raises:
            ValidationError: If the value is not a boolean.

        Returns:
            bool: The validated is_verified value.
        """
        _ = kwargs
        if not isinstance(value, bool):
            raise ValidationError("is_verified must be a boolean.")
        return value

    @validates('language')
    def validate_language(self, value, **kwargs):
        """
        Validate that the language does not exceed 10 characters.

        Args:
            value (str): The language to validate.

        Raises:
            ValidationError: If the language exceeds 10 characters.

        Returns:
            str: The validated language.
        """
        _ = kwargs
        if value and len(value) > 10:
            raise ValidationError("Language cannot exceed 10 characters.")
        return value

    @validates('company_id')
    def validate_company_id(self, value, **kwargs):
        """
        Validate that the company_id is a valid UUID string and exists.

        Args:
            value (str): The company_id to validate.

        Raises:
            ValidationError: If the company_id is not a valid UUID or does
                not exist.

        Returns:
            str: The validated company_id.
        """
        _ = kwargs
        if not isinstance(value, str):
            raise ValidationError("company_id must be a string (UUID).")
        try:
            if not check_company_id(value):
                raise ValidationError("Invalid company_id.")
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return value

    @validates('role_id')
    def validate_role_id(self, value, **kwargs):
        """
        Validate that the role_id is a non-negative integer and exists.

        Args:
            value (int): The role_id to validate.

        Raises:
            ValidationError: If the role_id is negative, not an integer,
                or invalid.

        Returns:
            int: The validated role_id.
        """
        _ = kwargs
        if not isinstance(value, int) or value < 0:
            raise ValidationError("role_id must be a non-negative integer.")
        if not check_role_id(value):
            raise ValidationError("Invalid role_id.")

        return value

    @validates('hashed_passwd')
    def validate_hashed_passwd(self, value, **kwargs):
        """
        Validate that the hashed password is not empty and does not exceed the
        maximum length.

        Args:
            value (str): The hashed password to validate.

        Raises:
            ValidationError: If the hashed password is empty or too long.

        Returns:
            str: The validated hashed password.
        """
        _ = kwargs
        if not value:
            raise ValidationError("Hashed password cannot be empty.")
        if len(value) > 256:
            raise ValidationError(
                "Hashed password cannot exceed 256 characters.")

        return value

    @validates('last_login_at')
    def validate_last_login_at(self, value, **kwargs):
        """
        Validate that the last login datetime is a valid datetime or ISO 8601
        string or None.

        Args:
            value (datetime, str or None): The last login datetime to validate.

        Raises:
            ValidationError: If the value is not a valid datetime or ISO 8601
                string or None.

        Returns:
            datetime or None: The validated last login datetime.
        """
        _ = kwargs
        if value is not None and not isinstance(value, (str, datetime)):
            raise ValidationError(
             "last_login_at must be a valid datetime, ISO8601 string, or None."
            )
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValidationError(
                    "last_login_at must be a valid ISO8601 datetime string."
                ) from exc
        return value
