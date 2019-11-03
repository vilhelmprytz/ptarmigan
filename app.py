###########################################################
#    __ _           _           _   _      _        _     #
#   / _| |         | |         | | (_)    | |      | |    #
#  | |_| | __ _ ___| | ________| |_ _  ___| | _____| |_   #
#  |  _| |/ _` / __| |/ /______| __| |/ __| |/ / _ \ __|  #
#  | | | | (_| \__ \   <       | |_| | (__|   <  __/ |_   #
#  |_| |_|\__,_|___/_|\_\       \__|_|\___|_|\_\___|\__|  #
#                                                         #
# Copyright (C) 2019, Vilhelm Prytz <vilhelm@prytznet.se> #
# https://github.com/VilhelmPrytz/flask-ticket            #
#                                                         #
###########################################################

from flask import Flask, render_template, redirect
from functools import wraps
from datetime import timedelta, datetime
from version import version
import string
import json

print(f"Running flask-ticket version {version}")

# Session
from flask_session.__init__ import Session

# flask app
app = Flask(__name__)

# read configuration
with open("config.json") as f:
    config = json.load(f)

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