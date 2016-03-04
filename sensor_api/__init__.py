#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("sensor_api.default_settings")
app.config.from_envvar("SENSOR_API_SETTINGS", silent=True)
db = SQLAlchemy(app)
manager = Manager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "web.login"

@app.context_processor
def inject_login_form():
    from .admin.forms import LoginForm
    return dict(g_form_login=LoginForm())

def run():
    # Setup migration
    Migrate(app, db)
    manager.add_command("db", MigrateCommand)

    # Load blueprints
    from .api import api_bp
    app.register_blueprint(api_bp)

    from .admin.controllers import web_bp
    app.register_blueprint(web_bp, url_prefix="/admin")

    manager.run()
