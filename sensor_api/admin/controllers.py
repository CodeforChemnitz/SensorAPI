import flask
import flask_login
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user

from . import forms
from sensor_api import models, db

web_bp = Blueprint("admin", __name__)

@web_bp.route("/", methods=["GET", "POST"])
def index():
    return render_template(
        "admin/index.html"
    )


@web_bp.route("/nodes/<int:node_id>", methods=["GET"])
@login_required
def node_details(node_id):
    user = flask_login.current_user
    node = models.SensorNode.query.filter_by(id=node_id, user=user).first()
    if not node:
        flask.abort(404)

    return render_template(
        "admin/nodes/details.html",
        sensor_node=node
    )


@web_bp.route("/nodes", methods=["GET"])
@login_required
def nodes():
    user = flask_login.current_user
    return render_template(
        "admin/nodes.html",
        sensor_nodes=user.sensor_nodes
    )

@web_bp.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm(request.form)
    if form.validate_on_submit():
        # ToDo: Use password and hash!!!!!!!!!!!!!!!!!
        user = models.User.query.filter_by(
            email=form.username.data,
            password=form.password.data
        ).first()
        if user:
            login_user(user)
            next_url = flask.request.args.get("next")
            # ToDo: check next url
            return flask.redirect(next_url or flask.url_for("admin.index"))

        flask.flash("Unable to login")

    return render_template(
        "login.html",
        form=form
    )

@web_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.index"))

@web_bp.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm(request.form)
    if form.validate_on_submit():
        print("foo")
        user = models.User(
            email=form.email.data,
            password=form.password.data,
        )
        user.approved = False
        # ToDo: change and send mail
        user.approval_code = "abc"
        db.session.add(user)
        db.session.commit()
        flash("User successfully registered")
        return redirect(url_for("admin.login"))

    return render_template("register.html", form=form)
