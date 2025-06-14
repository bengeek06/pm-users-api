"""
models.py
---------

This module defines the SQLAlchemy database models for the application.
"""
import uuid
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """
    Data model for the User entity.

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
        company_id (str): Company ID associated with the User.
        role_id (int): Role ID associated with the User.
        last_login_at (datetime): Last login datetime.
        created_at (datetime): Creation datetime.
        updated_at (datetime): Last update datetime.
    """
    __tablename__ = 'users'

    id = db.Column(db.String(40), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_passwd = db.Column(db.String(256), nullable=False)
    firstname = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    avatar_url = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    language = db.Column(db.String(10), nullable=True)
    company_id = db.Column(db.String(40), nullable=False, default=0)
    role_id = db.Column(db.Integer, nullable=False, default=0)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
        )

    def __repr__(self):
        """
        Return a string representation of the User instance.

        Returns:
            str: String representation of the User.
        """
        return (
            f"<User {self.email}>"
            f" (ID: {self.id}, Email: {self.email}, "
            f"First Name: {self.firstname}, Last Name: {self.lastname}, "
            f"Phone: {self.phone_number}, Active: {self.is_active}, "
            f"Verified: {self.is_verified}, Language: {self.language}, "
            f"Company ID: {self.company_id}, Role ID: {self.role_id}, "
            f"Last Login: {self.last_login_at}, "
            f"Created At: {self.created_at}, Updated At: {self.updated_at})"
        )

    @classmethod
    def get_all(cls):
        """
        Retrieve all User records from the database.

        Returns:
            list: List of all User objects.
        """
        return cls.query.all()

    @classmethod
    def get_by_id(cls, user_id):
        """
        Retrieve a User record by its ID.

        Args:
            user_id (str): ID of the User entity to retrieve.

        Returns:
            User: The User object with the given ID, or None if not found.
        """
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """
        Retrieve a User record by its email.

        Args:
            email (str): Email of the User entity to retrieve.

        Returns:
            User: The User object with the given email, or None if not found.
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def create(
        cls,
        email,
        hashed_passwd,
        firstname=None,
        lastname=None,
        phone_number=None,
        avatar_url=None,
        is_active=True,
        is_verified=False,
        language=None,
        company_id=0,
        role_id=0,
        user_id=None
    ):
        """
        Create a new User record.

        Args:
            email (str): Email address of the User.
            hashed_passwd (str): Hashed password of the User.
            firstname (str, optional): First name of the User.
            lastname (str, optional): Last name of the User.
            phone_number (str, optional): Phone number of the User.
            avatar_url (str, optional): Avatar URL of the User.
            is_active (bool, optional): Whether the User is active.
            is_verified (bool, optional): Whether the User is verified.
            language (str, optional): Preferred language of the User.
            company_id (str, optional): Company ID associated with the User.
            role_id (int, optional): Role ID associated with the User.

        Returns:
            User: The newly created User object.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        if cls.get_by_email(email):
            raise ValueError(f"User with email {email} already exists.")

        if not user_id:
            user_id = uuid.uuid4().hex

        user = cls(
            id=user_id,
            email=email,
            hashed_passwd=hashed_passwd,
            firstname=firstname,
            lastname=lastname,
            phone_number=phone_number,
            avatar_url=avatar_url,
            is_active=is_active,
            is_verified=is_verified,
            language=language,
            company_id=company_id,
            role_id=role_id
        )

        db.session.add(user)
        db.session.commit()
        return user

    def update(
        self,
        email=None,
        hashed_passwd=None,
        firstname=None,
        lastname=None,
        phone_number=None,
        avatar_url=None,
        is_active=None,
        is_verified=None,
        language=None,
        company_id=None,
        role_id=None,
        last_login_at=None
    ):
        """
        Update the attributes of the User entity.

        Args:
            email (str, optional): New email address.
            hashed_passwd (str, optional): New hashed password.
            firstname (str, optional): New first name.
            lastname (str, optional): New last name.
            phone_number (str, optional): New phone number.
            avatar_url (str, optional): New avatar URL.
            is_active (bool, optional): New active status.
            is_verified (bool, optional): New verification status.
            language (str, optional): New language.
            company_id (str, optional): New company ID.
            role_id (int, optional): New role ID.
            last_login_at (datetime, optional): New last login datetime.

        Raises:
            ValueError: If the new email is already used by another user.
        """
        if email is not None:
            if self.get_by_email(email) and self.email != email:
                raise ValueError(f"User with email {email} already exists.")
            self.email = email
        if hashed_passwd is not None:
            self.hashed_passwd = hashed_passwd
        if firstname is not None:
            self.firstname = firstname
        if lastname is not None:
            self.lastname = lastname
        if phone_number is not None:
            self.phone_number = phone_number
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if is_active is not None:
            self.is_active = is_active
        if is_verified is not None:
            self.is_verified = is_verified
        if language is not None:
            self.language = language
        if company_id is not None:
            self.company_id = company_id
        if role_id is not None:
            self.role_id = role_id
        if last_login_at is not None:
            self.last_login_at = last_login_at

        db.session.commit()

    def delete(self):
        """
        Delete the User record from the database.
        """
        db.session.delete(self)
        db.session.commit()
