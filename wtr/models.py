from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from passlib.hash import argon2

from . import db

class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(16), nullable=False, unique=True)
    _password = db.Column('password', db.String(73), nullable=False)

    email = db.Column(db.String(40), nullable=False, unique=True)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    phone = db.Column(db.String(10), nullable=False, unique=True)
    phone_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    created = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    # Map User.password to User._password
    @hybrid_property
    def password(self):
        return self._password

    # Store the hash of a password, not the plaintext
    @password.setter
    def password(self, plaintext):
        self._password = argon2.hash(plaintext)

    # Validate a password with the stored hash
    def validate_password(self, plaintext):
        return argon2.verify(plaintext, self._password)
