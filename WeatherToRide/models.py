
from . import db

from flask_login import UserMixin

from passlib.hash import argon2

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import TIME
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import datetime

class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String(32), nullable=False, unique=True)
    email_confirmed = Column(Boolean, nullable=False, default=False)

    _password = Column('password', String(73), nullable=False)

    name = Column(String(32), nullable=False)

    phone = Column(String(10), nullable=False, unique=True)
    phone_confirmed = Column(Boolean, nullable=False, default=False)

    locations = relationship('Location', backref='user', lazy=True)

    routes = relationship('Route', backref='user', lazy=True)

    created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

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

class Location(db.Model):

    __tablename__ = 'location'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    name = Column(String(32), nullable=False)

    lat = Column(DECIMAL(precision=10, scale=6), nullable=False)
    lng = Column(DECIMAL(precision=10, scale=6), nullable=False)

    forecast = relationship('Forecast', backref='location', lazy=True, uselist=False)

class Route(db.Model):

    __tablename__ = 'route'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    name = Column(String(32), nullable=False)

    location_1 = Column(Integer, ForeignKey('location.id'), nullable=False)
    location_2 = Column(Integer, ForeignKey('location.id'), nullable=False)

    time = Column(TIME(), nullable=False)

    mon = Column(Boolean, nullable=False, default=False)
    tue = Column(Boolean, nullable=False, default=False)
    wed = Column(Boolean, nullable=False, default=False)
    thu = Column(Boolean, nullable=False, default=False)
    fri = Column(Boolean, nullable=False, default=False)
    sat = Column(Boolean, nullable=False, default=False)
    sun = Column(Boolean, nullable=False, default=False)

class Forecast(db.Model):

    __tablename__ = 'forecast'

    id = Column(Integer, primary_key=True, autoincrement=True)

    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)

    day_0_icon = Column(String(32))
    day_0_summary = Column(String(255))
    day_0_recommendation = Column(String(255))

    day_1_icon = Column(String(32))
    day_1_summary = Column(String(255))
    day_1_recommendation = Column(String(255))

    day_2_icon = Column(String(32))
    day_2_summary = Column(String(255))
    day_2_recommendation = Column(String(255))

    day_3_icon = Column(String(32))
    day_3_summary = Column(String(255))
    day_3_recommendation = Column(String(255))

    day_4_icon = Column(String(32))
    day_4_summary = Column(String(255))
    day_4_recommendation = Column(String(255))

    day_5_icon = Column(String(32))
    day_5_summary = Column(String(255))
    day_5_recommendation = Column(String(255))

    day_6_icon = Column(String(32))
    day_6_summary = Column(String(255))
    day_6_recommendation = Column(String(255))

    day_7_icon = Column(String(32))
    day_7_summary = Column(String(255))
    day_7_recommendation = Column(String(255))

    updated = Column(DateTime(timezone=True), nullable=False)
