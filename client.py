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

client_routes = Blueprint('client_routes', __name__, template_folder='templates')

@client_routes.route('/')
def index():
    return ""