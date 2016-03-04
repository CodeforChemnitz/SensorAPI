import json
import os
from datetime import datetime
from functools import wraps
from hashlib import sha256
from uuid import uuid4
from flask import request, Response
from flask_restful import Resource

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

# this module
from sensor_api.models import User, SensorNode, SensorReading, SensorReadingType, SensorReadingCollection

from sensor_api import db, app

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


def check_api_version_header(f):
    """
    Checks the HTTP header for the presence of X-Sensor-Version and the value
    "1" otherwise returns with HTTP 406 Not Acceptable
    :param f:
    :return:
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if "X-Sensor-Version" not in request.headers:
            return Response("No version header provided", 406)
        if request.headers["X-Sensor-Version"] != "1":
            return Response("Wrong api version", 406)
        return f(*args, **kwargs)

    return decorated


class ApiResource(Resource):
    method_decorators = [check_api_version_header]


class UsersResource(ApiResource):
    def post(self):
        data = request.json
        if not data or ("email" not in data and "password" not in data):
            return {"message": '"email" and "password" are needed'}, 422

        salt = uuid4().hex
        password_hash = sha256((salt + data["password"]).encode("utf-8"))
        user = User(
            email=data["email"],
            password=salt + password_hash.hexdigest()
        )
        if os.environ.get("CI") != None:
            user.approval_code = "testing_approval_code"

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            return {"message": "email address already in use"}, 409

        return {"id": user.id, "email": user.email, "created_at": str(user.created_at)}


class UserConfimResource(Resource):
    def get(self, id, approval_code):
        try:
            user = db.session.query(User).\
                filter(User.id == id).\
                filter(User.approval_code == approval_code).\
                one()
            user.approval_code = None
            user.approved = True

            db.session.commit()

            return {"message": "User email confirmed"}
        except NoResultFound:
            return {"message": "User not found"}, 400


class SensorsResource(ApiResource):
    def post(self):
        data = request.data.decode("utf-8")
        data = json.loads(data)

        try:
            user = db.session.query(User).\
                filter(User.email == data.get("email")).\
                filter(User.approved == True).\
                one()
            sensor = SensorNode(
                user=user,
                name=data.get("name")
            )
            if os.environ.get("CI") != None:
                sensor.api_key = "testing_api_key"

            db.session.add(sensor)
            try:
                db.session.commit()
            except ValueError:
                return {"message": "Sensor name is invalid"}, 400

            sensor_info = {
                "id": sensor.api_id.hex,
                "key": sensor.api_key.hex
            }

            return Response(
                json.dumps(sensor_info),
                status=200,
                mimetype="application/json"
            )
        except NoResultFound:
            return {"message": "User not found or not approved"}, 412


class SensorValuesResource(ApiResource):
    def post(self, sensor_id):
        if "X-Sensor-Api-Key" not in request.headers:
            return {"message": "No API key in header found"}, 401

        sensor_node = db.session.query(SensorNode).filter(SensorNode.api_id == sensor_id).one()
        if sensor_node.api_key.hex != request.headers["X-Sensor-Api-Key"]:
            return {"message": "Invalid API key"}, 401

        utc_now = datetime.utcnow()
        sensor_node.last_seen_at = utc_now

        data = request.data.decode("utf-8")
        data = json.loads(data)

        reading_types = sensor_node.reading_types
        for reading in data:
            idx, sensor_type, value_type, value = reading
            found = False
            for reading_type in reading_types:
                if reading_type.sensor_index == idx and \
                        reading_type.sensor_type == sensor_type and \
                        reading_type.value_type == value_type:
                    reading_type.last_seen_at = utc_now
                    found = True
                    break

            if not found:
                reading_type = SensorReadingType(
                    sensor_node=sensor_node,
                    sensor_index=idx,
                    sensor_type=sensor_type,
                    value_type=value_type,
                    last_seen_at=utc_now
                )
                db.session.add(reading_type)

        collection = SensorReadingCollection(sensor_node=sensor_node)
        db.session.add(collection)
        for reading in data:
            idx, sensor_type, value_type, value = reading

            sensor_reading = SensorReading(
                sensor_index=idx,
                sensor_type=sensor_type,
                value_type=value_type,
                value=value,
                collection=collection
            )
            db.session.add(sensor_reading)

        db.session.commit()

        return {}
