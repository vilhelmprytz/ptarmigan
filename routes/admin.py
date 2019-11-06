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
from flask import Blueprint, render_template, request, redirect, session
from components.models import Admin, Message, Ticket
from components.models import db

# tools/specific for this blueprint
from components.decorators import admin_login_required
from components.tools import is_integer

# blueprint init
admin_routes = Blueprint('admin_routes', __name__, template_folder='../templates')
BASEPATH = '/admin'

# routes
@admin_routes.route(BASEPATH)
@admin_login_required
def index():
    return render_template("admin/dashboard.html")

@admin_routes.route(BASEPATH + "/tickets")
@admin_login_required
def tickets():
    tickets = Ticket.query.filter_by(status=0).order_by(Ticket.id.desc())
    return render_template("admin/tickets.html", tickets=tickets)

@admin_routes.route(BASEPATH + "/tickets/<id>")
@admin_login_required
def view_ticket(id):
    if not is_integer(id):
        return "id has to be integer", 400
    
    ticket = Ticket.query.get(id)
    messages = Message.query.filter_by(ticket_id=int(id))

    return render_template("admin/view_ticket.html", ticket=ticket, messages=messages)

@admin_routes.route(BASEPATH + "/login", methods=["POST", "GET"])
def admin_login():
    if request.method == "POST":
        data = request.form

        # validation check
        for key, value in data.items():
            if key != "email" and key != "password":
                return "at least one invalid key", 400
        
            if len(value) < 3:
                return f"{key} is too short", 400
                
            if key == "email":
                if len(value) > 50:
                    return f"value {value} of key {key} is too long", 400
                if "@" not in value:
                    return f"value {value} of key {key} is missing @", 400
                if "." not in value:
                    return f"value {value} of key {key} is missing .", 400
        
        # check authentication
        admin = Admin.query.filter_by(email=data["email"])[0] # should always only be one admin with this name

        # verify
        if Admin.verify_password(admin.hashed_password, data["password"]):
            session["admin_logged_in"] = True
        else:
            session["admin_logged_in"] = False
            return redirect(BASEPATH + "/login?fail=true")
        
        return redirect(BASEPATH)
        
    elif request.method == "GET":
        return render_template("admin/login.html")

@admin_routes.route(BASEPATH + "/logout")
def admin_logout():
    session.pop("admin_logged_in")

    return redirect(BASEPATH)