# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api, Resource

from . import controllers

api_bp = Blueprint("api", __name__)
api = Api(api_bp)


class ApiResource(Resource):
    """
    Handle the root node of the Rest API
    """
    def get(self):
        """
        Return a list of available API versions

        :return: List of available API versions
        :rtype: str[]
        """
        return ["v1"]


api.add_resource(ApiResource, "/")
api.add_resource(controllers.UsersResource, "/v1/users")
api.add_resource(controllers.UserConfimResource, "/v1/users/<int:id>/<approval_code>")
api.add_resource(controllers.SensorNodes, "/v1/nodes")
api.add_resource(controllers.SensorNodeMetrics, "/v1/nodes/<node_id>/metrics")
