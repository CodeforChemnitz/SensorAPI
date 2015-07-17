#!/bin/env python3


from flask import Flask, request, abort, Response
from functools import wraps
from uuid import uuid4
from hashlib import sha256
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError

# this module
from sqlalchemy.orm.exc import NoResultFound
from database import db_session, init_db
from models import User, Sensor, SensorValue, SensorType


app = Flask(__name__)
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

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

@app.route("/users", methods=['POST'])
@check_api_version_header
def add_users():
    data = request.json
    if not data or ("email" not in data and "password" not in data):
        abort(422)

    salt = uuid4().hex
    password_hash = sha256((salt + data["password"]).encode('utf-8')).hexdigest()
    user = User(
        email=data["email"],
        password=salt + password_hash
    )
    db_session.add(user)
    try:
        db_session.commit()
    except IntegrityError:
        abort(409)

    return jsonify(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        approved=user.approved
    )

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
        user = db_session.query(User).\
            filter(User.email == data.get("email")).\
            filter(User.approved == True).\
            one()
        sensor = Sensor(
            user=user,
            name=data.get("name")
        )

        db_session.add(sensor)
        try:
            db_session.commit()
        except ValueError:
            abort(409)

        return "id:%s\napikey:%s" % (sensor.id, sensor.api_key)
    except NoResultFound:
        abort(412)


@app.route("/sensors/<sensor_id>", methods=['POST'])
@check_api_version_header
def add_sensor_value(sensor_id):
    if "X-Sensor-Api-Key" not in request.headers:
        abort(401)

    sensor = db_session.query(Sensor).filter(Sensor.id == sensor_id).one()
    if sensor.api_key != request.headers["X-Sensor-Api-Key"]:
        abort(401)

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
        return Response("Bad csv lines:\n" + "\n".join(bad), 400)

    return ""


if __name__ == "__main__":
    app.run(debug=True)
