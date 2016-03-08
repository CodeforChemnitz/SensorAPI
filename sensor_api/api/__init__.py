# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api

from . import controllers

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(controllers.UsersResource, "/v1/users")
api.add_resource(controllers.UserConfimResource, "/v1/users/<int:id>/<approval_code>")
api.add_resource(controllers.SensorNodes, "/v1/nodes")
api.add_resource(controllers.SensorNodeMetrics, "/v1/nodes/<node_id>/metrics")
