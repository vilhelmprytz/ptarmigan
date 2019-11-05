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
from components.tools import is_integer, random_string

# blueprint init
client_routes = Blueprint('client_routes', __name__, template_folder='../templates')

# routes
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
            ticket = Ticket(name=data["name"], email=data["email"], client_key=random_string(length = 15), status=0)
            db.session.add(ticket)
            db.session.flush()
            message = Message(message=data["message"], sender_id=0, ticket_id=ticket.id) # sender_id=0 will always be client in conversation
            db.session.add(message)
        except Exception as err:
            return f"error occured, {err}"

        # commit
        try:
            db.session.commit()
        except Exception as err:
            return f"error occured, {err}"

        return redirect(f'/ticket?id={ticket.id}&key={ticket.client_key}')

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
    ticket = Ticket.query.get(data["id"])

    if ticket.client_key != data["key"]:
        return "invalid secret key", 400

    messages = Message.query.filter_by(ticket_id=data["id"])

    return render_template("client/ticket.html", ticket=ticket, messages=messages)
