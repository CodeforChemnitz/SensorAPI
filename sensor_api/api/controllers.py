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

from sensor_api import db, app, models

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


def jsonp_wrapper(func):
    """
    Wraps JSONified output for JSONP requests.

    :param func: Wrapped function
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = func(*args, **kwargs)
            data = json.dumps(data, indent=1)
            content = str(callback) + "(" + data + ")"
            mimetype = "application/javascript"
            return app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


class ApiResource(Resource):
    method_decorators = [jsonp_wrapper]


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


class UserConfimResource(ApiResource):
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


class SensorNodes(ApiResource):
    def get(self):
        nodes = []
        for node in models.SensorNode.query.all():
            node_data = {
                "id": node.api_id.hex
            }

            if node.geo_latitude and node.geo_longitude:
                # ToDo: encode Decimal()
                # ToDo: use fields
                node_data["geo_lat"] = float(node.geo_latitude)
                node_data["geo_lng"] = float(node.geo_longitude)

            nodes.append(node_data)
        return nodes

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


class SensorNodeMetrics(ApiResource):
    def post(self, node_id):
        if "X-Sensor-Api-Key" not in request.headers:
            return {"message": "No API key in header found"}, 401

        sensor_node = db.session.query(SensorNode).filter(SensorNode.api_id == node_id).one()
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

        """
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
        """
        db.session.commit()

        metrics = []
        for reading in data:
            idx, sensor_type, value_type, value = reading
            metrics.append({
                "measurement": "temp",
                "tags": {
                    # Node Id
                    "ni": sensor_node.id,
                    # Sensor Id
                    "si": idx
                },
                "time": utc_now.isoformat(),
                "fields": {
                    "value": value
                }
            })

        from influxdb import InfluxDBClient
        client = InfluxDBClient(
            host="localhost",
            port=8086,
            database="metrics"
        )
        client.write_points(metrics)

        return {}
