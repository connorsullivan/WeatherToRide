from . import db
from flask_login import UserMixin

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

from passlib.hash import argon2

class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String(40), nullable=False, unique=True)
    email_confirmed = Column(Boolean, nullable=False, default=False)

    _password = Column('password', String(73), nullable=False)

    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)

    phone = Column(String(10), nullable=False, unique=True)
    phone_confirmed = Column(Boolean, nullable=False, default=False)

    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return '<User {}>'.format(self.id)

    # Map password to _password
    @hybrid_property
    def password(self):
        return self._password

    # Hash the password before storing it
    @password.setter
    def password(self, plaintext):
        self._password = argon2.hash(plaintext)

    # Check a plaintext candidate against the stored hash
    def validate_password(self, plaintext):
        return argon2.verify(plaintext, self._password)
