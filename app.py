###########################################################
#         _                       _                       #
#        | |                     (_)                      #
#   _ __ | |_ __ _ _ __ _ __ ___  _  __ _  __ _ _ __      #
#  | '_ \| __/ _` | '__| '_ ` _ \| |/ _` |/ _` | '_ \     #
#  | |_) | || (_| | |  | | | | | | | (_| | (_| | | | |    #
#  | .__/ \__\__,_|_|  |_| |_| |_|_|\__, |\__,_|_| |_|    #
#  | |                               __/ |                #
#  |_|                              |___/                 #
#                                                         #
# Copyright (C) 2019, Vilhelm Prytz <vilhelm@prytznet.se> #
# https://github.com/VilhelmPrytz/ptarmigan               #
#                                                         #
###########################################################

from flask import Flask, render_template, redirect
from datetime import timedelta, datetime
from version import version
import string

from components.tools import read_configuration

print(f"Running ptarmigan version {version}")

# Session
from flask_session.__init__ import Session

# flask app
app = Flask(__name__)

# read configuration
config = read_configuration()

# SQL
mysql_password = ":" + config["mysql"]["password"]
if config["mysql"]["password"] == "": # if password is empty
    mysql_password = ""

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{config["mysql"]["username"]}{mysql_password}@{config["mysql"]["host"]}/{config["mysql"]["database"]}'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

from components.models import db

db.init_app(app)

with app.app_context():
    db.create_all()

# Session Management
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = config["settings"]["session_path"]
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

app.config.from_object(__name__)
Session(app)

# error handler
@app.errorhandler(400)
def error_400(e):
    return render_template("errors/400.html"), 400

@app.errorhandler(404)
def error_404(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def error_500(e):
    return render_template("errors/500.html"), 500

# register routes
from routes.client import client_routes
from routes.admin import admin_routes

app.register_blueprint(client_routes)
app.register_blueprint(admin_routes)

# run app
if __name__ == '__main__':
    app.run(host="0.0.0.0")