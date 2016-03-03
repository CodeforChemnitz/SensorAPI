#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("sensor_api.default_settings")
app.config.from_envvar("SENSOR_API_SETTINGS", silent=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)

def run():
    #db.init_db()
    #app.run(host='0.0.0.0', threaded=True)
    from .api import api_bp
    app.register_blueprint(api_bp)
    manager.run()
