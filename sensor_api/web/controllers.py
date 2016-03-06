import json

import flask

from .. import models

web_bp = flask.Blueprint("web", __name__)


@web_bp.route("/", methods=["GET", "POST"])
def index():
    return flask.render_template(
        "web/index.html"
    )


@web_bp.route("/locations", methods=["GET"])
def locations():
    nodes = {}
    for node in models.SensorNode.query.all():
        if not node.geo_latitude or not node.geo_longitude:
            continue

        # ToDo: encode Decimal()
        nodes[node.id] = {
            "geo_lat": float(node.geo_latitude),
            "geo_lng": float(node.geo_longitude)
        }
    return json.dumps(nodes)