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

from flask import Blueprint

admin_routes = Blueprint('admin_routes', __name__, template_folder='../templates')

BASEPATH = '/admin'

@admin_routes.route(BASEPATH)
def index():
    return ""

@admin_routes.route(BASEPATH + "/login")
def admin_login():
    return ""