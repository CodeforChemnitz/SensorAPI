#!/bin/env python3

from flask import Flask, request, abort, Response
from functools import wraps
from uuid import uuid4

app = Flask(__name__)

class NoUserException(Exception):
    pass
class InvalidSensorType(Exception):
    pass

class Value(object):
    _uuid = None
    _id = None
    _type = None
    _value = None

    def __init__(self, uuid, id, type, value):
        self._uuid = uuid
        self._id = id
        self._type = get_type(type)
        self._value = value

    def save(self):
        # TODO save to database
        pass

class User(object):
    def __init__(self, email):
        pass

    def get_id(self):
        return 1

class Sensor(object):
    def __init__(self, user, name):
        pass

    def get_api_key(self):
        return str(uuid4().hex)

    def get_uuid(self):
        return str(uuid4().hex)

def get_user(email):
    # TODO check DB for email addresses
    if email != "test@example.org":
        raise NoUserException

    return User(email)

def get_type(type):
    # TODO check DB for sensor types
    if type not in [1, 2, 3]:
        raise InvalidSensorType

    return type

def check_api_version_header(f):
    """
    Checks the HTTP header for the presence of X-Sensor-Version and the value "1" otherwise returns with HTTP 406 Not
    Acceptable
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

def check_api_key(uuid, apikey):
    # TODO check for correct uuid and apikey in DB
    return uuid == 'def' and apikey == 'abc'

@app.route("/sensors", methods=['POST'])
@check_api_version_header
def add_sensor():
    data = {}
    for line in request.data.decode("utf-8").split("\n"):
        try:
            (name, value) = line.split(":", 1)
            if name in ["email", "name"]:
                data[name] = value
        except ValueError:
            pass

    try:
        user = get_user(data.get("email"))
        sensor = Sensor(user, data.get("name"))
        return "uuid:%s\napikey:%s" % (sensor.get_uuid(), sensor.get_api_key())
    except NoUserException:
        abort(412)

@app.route("/sensors/<uuid>", methods=['POST'])
@check_api_version_header
def add_sensor_value(uuid):
    print(request.headers)
    if "X-Sensor-Api-Key" not in request.headers or \
        not check_api_key(uuid, request.headers["X-Sensor-Api-Key"]):
        abort(401)

    bad = []
    for line in request.data.decode("utf-8").split("\n"):
        try:
            (id, type, value) = line.split(",")
            sensor_value = Value(uuid, int(id), int(type), float(value))
            sensor_value.save()
        except ValueError:
            bad.append(line + " invalid format: id(int),type(int),value(float) required")
        except InvalidSensorType:
            bad.append(line + " invalid sensor type")

    if len(bad) > 0:
        return Response("Bad csv lines:\n" + "\n".join(bad), 400)

    return ""

if __name__ == "__main__":
    app.run(debug=True)