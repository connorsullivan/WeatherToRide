
from . import db

from flask_login import UserMixin

from passlib.hash import argon2

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

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

    dev = relationship('Developer', backref='user', lazy=True, uselist=False)

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

    # Serialize method for JSON API
    def serialize(self):
        return { 
            "id": self.id, 
            "email": self.email, 
            "email_confirmed": self.email_confirmed, 
            "password": self.password, 
            "name": self.name, 
            "phone": self.phone, 
            "phone_confirmed": self.phone_confirmed, 
            "locations": len(self.locations), 
            "routes": len(self.routes) 
        }

class Location(db.Model):

    __tablename__ = 'location'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    lat = Column(DECIMAL(precision=10, scale=6), nullable=False)
    lng = Column(DECIMAL(precision=10, scale=6), nullable=False)

    name = Column(String(32), nullable=False)

    forecast = relationship('Forecast', backref='location', lazy=True, uselist=False)

    # Serialize method for JSON API
    def serialize(self):
        return { 
            "locationId": self.id, 
            "locationLat": float(self.lat), 
            "locationLng": float(self.lng), 
            "locationName": self.name 
        }

class Route(db.Model):

    __tablename__ = 'route'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    location_id_1 = Column(Integer, ForeignKey('location.id'), nullable=False)
    location_id_2 = Column(Integer, ForeignKey('location.id'), nullable=False)

    name = Column(String(32), nullable=False)

    mon = Column(Boolean, nullable=False, default=False)
    tue = Column(Boolean, nullable=False, default=False)
    wed = Column(Boolean, nullable=False, default=False)
    thu = Column(Boolean, nullable=False, default=False)
    fri = Column(Boolean, nullable=False, default=False)
    sat = Column(Boolean, nullable=False, default=False)
    sun = Column(Boolean, nullable=False, default=False)

    # Serialize method for JSON API
    def serialize(self):

        days = []

        if self.mon:
            days.append('monday')
        if self.tue:
            days.append('tuesday')
        if self.wed:
            days.append('wednesday')
        if self.thu:
            days.append('thursday')
        if self.fri:
            days.append('friday')
        if self.sat:
            days.append('saturday')
        if self.sun:
            days.append('sunday')

        return { 
            "routeId": self.id, 
            "routeLocation1": self.location_id_1, 
            "routeLocation2": self.location_id_2, 
            "routeName": self.name, 
            "routeDays": days 
        }

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

    updated_at = Column(DateTime(timezone=True))

    # Serialize method for JSON API
    def serialize(self):

        days = []

        days.append({ "icon": self.day_0_icon, "summary": self.day_0_summary, "recommendation": self.day_0_recommendation })
        days.append({ "icon": self.day_1_icon, "summary": self.day_1_summary, "recommendation": self.day_1_recommendation })
        days.append({ "icon": self.day_2_icon, "summary": self.day_2_summary, "recommendation": self.day_2_recommendation })
        days.append({ "icon": self.day_3_icon, "summary": self.day_3_summary, "recommendation": self.day_3_recommendation })
        days.append({ "icon": self.day_4_icon, "summary": self.day_4_summary, "recommendation": self.day_4_recommendation })
        days.append({ "icon": self.day_5_icon, "summary": self.day_5_summary, "recommendation": self.day_5_recommendation })
        days.append({ "icon": self.day_6_icon, "summary": self.day_6_summary, "recommendation": self.day_6_recommendation })

        return { 
            "forecastDays": days, 
            "lastUpdate": self.updated_at.isoformat() 
        }

class API(db.Model):

    __tablename__ = 'api'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(32), nullable=False)

    calls_today = Column(Integer, nullable=False)
    calls_total = Column(Integer, nullable=False)

    last_reset = Column(DateTime(timezone=True), nullable=False)

class Developer(db.Model):

    __tablename__ = 'developer'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    key = Column(String(32), nullable=False)
