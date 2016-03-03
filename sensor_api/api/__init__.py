# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api

from sensor_api.api.controllers import UsersResource, UserConfimResource, SensorsResource, SensorValuesResource

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(UsersResource, "/users")
api.add_resource(UserConfimResource, "/users/<int:id>/<approval_code>")
api.add_resource(SensorsResource, "/sensors")
api.add_resource(SensorValuesResource, "/sensors/<sensor_id>")
