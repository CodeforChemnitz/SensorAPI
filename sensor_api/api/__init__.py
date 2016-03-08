# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api

from . import controllers

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(controllers.UsersResource, "/users")
api.add_resource(controllers.UserConfimResource, "/users/<int:id>/<approval_code>")
api.add_resource(controllers.SensorNodes, "/nodes")
api.add_resource(controllers.SensorNodeMetrics, "/nodes/<node_id>/metrics")
