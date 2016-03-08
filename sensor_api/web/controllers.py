import flask

web_bp = flask.Blueprint("web", __name__)


@web_bp.route("/", methods=["GET", "POST"])
def index():
    return flask.render_template(
        "web/index.html"
    )
