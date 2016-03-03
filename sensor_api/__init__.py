#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("sensor_api.default_settings")
app.config.from_envvar("SENSOR_API_SETTINGS", silent=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
api = Api(app)

from sensor_api.controllers import UsersResource, UserConfimResource, SensorsResource, SensorValuesResource

api.add_resource(UsersResource, "/users")
api.add_resource(UserConfimResource, "/users/<int:id>/<approval_code>")
api.add_resource(SensorsResource, "/sensors")
api.add_resource(SensorValuesResource, "/sensors/<sensor_id>")

def run():
    #db.init_db()
    #app.run(host='0.0.0.0', threaded=True)
    manager.run()
