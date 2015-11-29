# -*- coding: utf-8 -*-

from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, backref

# this module
from sensor_api import db
from sensor_api.helper.db_types import GUID


class User(db.Model):
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


class SensorNode(db.Model):
    __tablename__ = 'sensor_nodes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    api_key = Column(GUID, default=lambda : uuid.uuid4(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref=backref("sensor_nodes", order_by=id))

    def __repr__(self):
        return "<SensorNode(name='%s', user='%s', api_key='%s')>" % (
            self.name, self.user, self.api_key)


class SensorType(db.Model):
    __tablename__ = 'sensortypes'

    id = Column(Integer, primary_key=True)
    name= Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<SensorType(name='%s')>" % (self.name)


class SensorValue(db.Model):
    __tablename__ = 'sensorvalues'

    id = Column(Integer, nullable=False, primary_key=True)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensor_nodes.id'), primary_key=True)
    sensor = relationship("SensorNode", backref=backref('values', order_by=created_at))
    type_id = Column(Integer, ForeignKey('sensortypes.id'), primary_key=True)
    type = relationship("SensorType")

    def __repr__(self):
        return "<SensorValue(sensor='%s', type='%s', value='%f')>" % (self.sensor, self.type.name, self.value)
