# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
# this module
from sensor_api.database import Base

def uuid():
    return str(uuid4().hex)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(96))  # 32 salt + 64 sha256
    approved = Column(Boolean, default=False)
    approval_code = Column(String(32), default=uuid)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<User(email='%s', password='%s', approved='%s')>" % (
            self.email, self.password, self.approved)

class Sensor(Base):
    __tablename__ = 'sensors'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref('sensors', order_by=id))
    name = Column(String(255))
    api_key = Column(String(32), default=uuid, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Sensor(name='%s', user='%s', api_key='%s')>" % (
            self.name, self.user, self.api_key)

class SensorType(Base):
    __tablename__ = 'sensortypes'

    id = Column(Integer, primary_key=True)
    name= Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<SensorType(name='%s')>" % (self.name)

class SensorValue(Base):
    __tablename__ = 'sensorvalues'

    id = Column(Integer, nullable=False, primary_key=True)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id'), primary_key=True)
    sensor = relationship("Sensor", backref=backref('values', order_by=created_at))
    type_id = Column(Integer, ForeignKey('sensortypes.id'), primary_key=True)
    type = relationship("SensorType")

    def __repr__(self):
        return "<SensorValue(sensor='%s', type='%s', value='%f')>" % (self.sensor, self.type.name, self.value)
