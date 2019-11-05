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

# main imports
from flask import Blueprint, render_template, request, redirect
from components.models import Admin, Message, Ticket
from components.models import db

# tools/specific for this blueprint

# blueprint init
admin_routes = Blueprint('admin_routes', __name__, template_folder='../templates')
BASEPATH = '/admin'

# routes

@admin_routes.route(BASEPATH)
def index():
    return ""

@admin_routes.route(BASEPATH + "/login")
def admin_login():
    return ""