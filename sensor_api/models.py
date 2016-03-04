# -*- coding: utf-8 -*-

from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, SmallInteger
from sqlalchemy.orm import relationship, backref

# this module
from sensor_api import db
from sensor_api.helper.db_types import GUID


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(96))  # 32 salt + 64 sha256
    approved = Column(Boolean, default=False)
    approval_code = Column(String(32), default=uuid)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User(email='%s', password='%s', approved='%s')>" % (
            self.email, self.password, self.approved)

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


class SensorNode(db.Model):
    __tablename__ = "sensor_nodes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    api_id = Column(GUID, default=lambda: uuid.uuid4(), nullable=False, unique=True)
    api_key = Column(GUID, default=lambda: uuid.uuid4(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref=backref("sensor_nodes", order_by=id))

    def __repr__(self):
        return "<SensorNode(name='%s', user='%s', api_key='%s')>" % (
            self.name, self.user, self.api_key)


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("sensor_reading_collections.id"))
    sensor_index = Column(SmallInteger, nullable=False)
    sensor_type = Column(SmallInteger, nullable=False)
    value_type = Column(SmallInteger, nullable=False)
    value = Column(Float, nullable=False)

    # Relationships
    #type = relationship("SensorType")

    def __repr__(self):
        return "<SensorReading(sensor='%s', type='%s', value='%f')>" % (self.sensor, self.type.name, self.value)


class SensorReadingCollection(db.Model):
    __tablename__ = "sensor_reading_collections"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sensor_node_id = Column(Integer, ForeignKey("sensor_nodes.id"))

    # Relationships
    sensor_node = relationship("SensorNode", backref=backref("reading_collections"))
    readings = relationship("SensorReading", backref=backref("collection"))

    def __repr__(self):
        return "<SensorReadingCollection(sensor='%s', type='%s', value='%f')>" % (self.sensor, self.type.name, self.value)
