#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from uuid import uuid4
from hashlib import sha256
import os

from flask import Flask, request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from flask_restful import Resource, Api

# this module
from database import db_session, init_db
from models import User, Sensor, SensorValue, SensorType


app = Flask(__name__)
api = Api(app)
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

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
            return {'message': '"email" and "password" are needed'}, 422

        salt = uuid4().hex
        password_hash = sha256((salt + data["password"]).encode('utf-8'))
        user = User(
            email=data["email"],
            password=salt + password_hash.hexdigest()
        )
        if os.environ.get('CI') != None:
            user.approval_code = 'testing_approval_code'

        db_session.add(user)
        try:
            db_session.commit()
        except IntegrityError:
            return {'message': 'email address already in use'}, 409

        return {'id': user.id, 'email': user.email, 'created_at': str(user.created_at)}

class UserConfimResource(Resource):
    def get(self, id, approval_code):
        try:
            user = db_session.query(User).\
                filter(User.id == id).\
                filter(User.approval_code == approval_code).\
                one()
            user.approval_code = None
            user.approved = True

            db_session.commit()

            return {'message': 'User email confirmed'}
        except NoResultFound:
            return {'message': 'User not found'}, 400

class SensorsResource(ApiResource):
    def post(self):
        data = {}
        for line in request.data.decode("utf-8").split("\n"):
            try:
                (name, value) = line.split(":", 1)
                if name in ["email", "name"]:
                    data[name] = value.strip()
            except ValueError:
                pass

        try:
            user = db_session.query(User).\
                filter(User.email == data.get("email")).\
                filter(User.approved == True).\
                one()
            sensor = Sensor(
                user=user,
                name=data.get("name")
            )
            if os.environ.get('CI') != None:
                sensor.api_key = 'testing_api_key'

            db_session.add(sensor)
            try:
                db_session.commit()
            except ValueError:
                return {'message': 'Sensor name is invalid'}, 400

            return Response(
                "id:%s\napikey:%s\n" % (sensor.id, sensor.api_key),
                status=200,
                mimetype='text/plain'
            )
        except NoResultFound:
            return {'message': 'User not found or not approved'}, 412


class SensorValuesResource(ApiResource):
    def post(self, sensor_id):
        if "X-Sensor-Api-Key" not in request.headers:
            return {'message': 'No API key in header found'}, 401

        sensor = db_session.query(Sensor).filter(Sensor.id == sensor_id).one()
        if sensor.api_key != request.headers["X-Sensor-Api-Key"]:
            return {'message': 'Invalid API key'}, 401

        valid_type_ids = [t[0] for t in db_session.query(SensorType.id).all()]

        bad = []
        for line in request.data.decode("utf-8").split("\n"):
            try:
                (id, type, value) = line.split(",")
                if int(type) not in valid_type_ids:
                    bad.append(line + " invalid sensor type")
                    continue

                value = SensorValue(
                    sensor=sensor,
                    id=int(id),
                    type_id=int(type),
                    value=float(value)
                )
                db_session.add(value)
                db_session.commit()
            except ValueError:
                bad.append(line + " invalid format: id(int),type(int),value(float) required")

        if len(bad) > 0:
            return {'message': 'Bad CSV lines', 'lines': bad}, 400

        return {}

api.add_resource(UsersResource, '/users')
api.add_resource(UserConfimResource, '/users/<int:id>/<approval_code>')
api.add_resource(SensorsResource, '/sensors')
api.add_resource(SensorValuesResource, '/sensors/<int:sensor_id>')

if __name__ == "__main__":
    app.run(debug=True)
