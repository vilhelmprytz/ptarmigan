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

from flask import Blueprint, render_template, request, redirect

import sys
sys.path.append('..')

from components.database import get_database_objects
from components.tools import is_integer

client_routes = Blueprint('client_routes', __name__, template_folder='../templates')

Tickets, Messages, Admins = get_database_objects()

@client_routes.route('/')
def index():
    return render_template("client/index.html")

@client_routes.route("/submit", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        data = request.form

        for key, value in data.items():
            if key != "name" and key != "email" and key != "message":
                return "at least one invalid key", 400
        
            if len(value) < 3:
                return f"{key} is too short", 400
            
            if key == "name":
                if len(value) > 50:
                    return f"value {value} of key {key} is too long", 400
                
            if key == "email":
                if len(value) > 50:
                    return f"value {value} of key {key} is too long", 400
                if "@" not in value:
                    return f"value {value} of key {key} is missing @", 400
                if "." not in value:
                    return f"value {value} of key {key} is missing .", 400
            
            if key == "message":
                if len(value) > 500:
                    return f"value {value} of key {key} is too long", 400
        
        # create objects
        try:
            ticket = Tickets.new(data["name"], data["email"], status=0)
            message = Messages.new(ticket["id"], data["message"], 0) # sender_id=0 will always be client in conversation
        except Exception as err:
            return f"error occured, {err}"

        return redirect(f'/ticket?id={ticket["id"]}&key={ticket["client_key"]}')

    if request.method == "GET":
        return render_template("client/submit.html")

@client_routes.route("/ticket")
def ticket():
    data = request.args

    if not data or len(data) < 2:
        return "missing arguments", 400

    for key, value in data.items():
        if key != "id" and key != "key":
            return "at least one invalid variable", 400

        if key == "id":
            if not is_integer(value):
                return "id must be integer", 400

        if key == "key":
            if len(value) != 15:
                return "secret key is invalid length", 400

    # check if secret_key is correct
    ticket = Tickets.get_id(id)

    if ticket["client_key"] != data["key"]:
        return "invalid secret key", 400

    messages = Messages.get_ticket_id(id)

    return render_template("client/ticket.html", ticket=ticket, messages=messages)
