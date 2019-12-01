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
from components.models import db, Admin, Message, Ticket

# tools/specific for this blueprint
from components.decorators import admin_login_required
from components.tools import is_integer, read_configuration
from components.update import check_for_new_releases
from sqlalchemy import or_
from version import version

# blueprint init
admin_routes = Blueprint("admin_routes", __name__, template_folder="../templates")

# blueprint global variables
BASEPATH = "/admin"
config = read_configuration()

# routes
@admin_routes.route(BASEPATH)
@admin_login_required
def index():
    tickets = Ticket.query.all()
    messages = Message.query.all()
    admins = Admin.query.all()

    return render_template(
        "admin/dashboard.html",
        name=config["settings"]["name"],
        num_tickets=len(tickets),
        num_messages=len(messages),
        num_admins=len(admins),
        version=version,
    )


@admin_routes.route(BASEPATH + "/system")
@admin_login_required
def system():
    status, new_release = check_for_new_releases()

    return render_template(
        "admin/system.html",
        name=config["settings"]["name"],
        status=status,
        new_release=new_release,
        version=version,
    )


@admin_routes.route(BASEPATH + "/tickets")
@admin_login_required
def tickets():
    data = request.args

    if data:
        if int(data["status"]) == 3:
            tickets = Ticket.query.filter_by(status=3).order_by(
                Ticket.time_updated.asc()
            )
            view_msg = "Viewing closed tickets"
        elif int(data["status"]) == 2:
            tickets = Ticket.query.filter_by(status=2).order_by(
                Ticket.time_updated.asc()
            )
            view_msg = "Viewing answered tickets"
    else:
        tickets = Ticket.query.filter(
            or_(Ticket.status.contains([0]), Ticket.status.contains([1]))
        ).order_by(Ticket.time_updated.asc())
        view_msg = "Viewing active tickets"

    return render_template(
        "admin/tickets.html",
        name=config["settings"]["name"],
        tickets=tickets,
        view_msg=view_msg,
    )


@admin_routes.route(BASEPATH + "/tickets/<id>")
@admin_login_required
def view_ticket(id):
    if not is_integer(id):
        return (
            render_template(
                "errors/custom.html", title="400", message="Id has to be integer."
            ),
            400,
        )

    ticket = Ticket.query.get(id)

    # if ticket does not exist in database
    if not ticket:
        return (
            render_template(
                "errors/custom.html", title="400", message="Ticket does not exist."
            ),
            400,
        )

    messages = Message.query.filter_by(ticket_id=int(id)).order_by(Message.id.desc())

    # build dict with admins
    admins = Admin.query.all()

    admin_names = {}

    for admin in admins:
        admin_names[admin.id] = admin.name

    return render_template(
        "admin/view_ticket.html",
        name=config["settings"]["name"],
        ticket=ticket,
        messages=messages,
        admin_names=admin_names,
        fail=request.args.get("fail"),
        success=request.args.get("success"),
    )


@admin_routes.route(BASEPATH + "/submitmessage", methods=["POST"])
@admin_login_required
def admin_submit_message():
    data = request.form

    # validation check
    for key, value in data.items():
        if key != "message" and key != "ticket_id":
            return redirect(
                BASEPATH + f"/tickets/{data['ticket_id']}?fail=Invalid keys were sent."
            )

        if key == "ticket_id":
            if not is_integer(value):
                return (
                    render_template(
                        "errors/custom.html",
                        title="400",
                        message="ticket_id has to be integer.",
                    ),
                    400,
                )

        if key == "message":
            if len(value) > 500:
                return redirect(
                    BASEPATH + f"/tickets/{data['ticket_id']}?fail=Message too long."
                )

            if len(value) < 3:
                return redirect(
                    BASEPATH + f"/tickets/{data['ticket_id']}?fail=Message too short."
                )

    # get ticket
    ticket = Ticket.query.get(int(data["ticket_id"]))

    try:
        message = Message(
            message=data["message"],
            sender_id=int(session.get("admin_user_id")),
            ticket_id=int(data["ticket_id"]),
        )
    except Exception:
        return (
            render_template(
                "errors/custom.html", title="400", message="Ticket ID does not exist."
            ),
            400,
        )

    # update status
    ticket.status = 2

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        return redirect(
            BASEPATH
            + f"/tickets/{data['ticket_id']}?fail=Server error, could not create message."
        )

    return redirect(BASEPATH + f'/tickets/{data["ticket_id"]}?success=Message sent!')


@admin_routes.route(BASEPATH + "/ticket_status", methods=["POST"])
@admin_login_required
def admin_ticket_status():
    data = request.form

    # validation check
    for key, value in data.items():
        if key != "ticket_id" and key != "status":
            return render_template(
                "errors/custom.html", title="400", message="Invalid keys were sent."
            )

        if not is_integer(value):
            return render_template(
                "errors/custom.html", title="400", message="Values have to be integers."
            )

    # get ticket
    try:
        ticket = Ticket.query.get(int(data["ticket_id"]))
    except Exception:
        return (
            render_template(
                "errors/custom.html", title="400", message="Ticket ID does not exist."
            ),
            400,
        )

    ticket.status = int(data["status"])

    try:
        db.session.commit()
    except Exception:
        return redirect(
            BASEPATH + f"/tickets/{ticket.id}?fail=Unable to update status."
        )

    return redirect(BASEPATH + f"/tickets/{ticket.id}?success=Status has been updated.")


@admin_routes.route(BASEPATH + "/login", methods=["POST", "GET"])
def admin_login():
    if request.method == "POST":
        data = request.form

        # validation check
        for key, value in data.items():
            if key != "email" and key != "password":
                return redirect(BASEPATH + "/login?fail=Invalid keys were sent.")

            if len(value) < 3:
                return redirect(BASEPATH + f"/login?fail={key} is too short.")

            if key == "email":
                if len(value) > 50:
                    return redirect(
                        BASEPATH + f"/login?fail=Value {value} of key {key} is too long"
                    )
                if "@" not in value:
                    return redirect(
                        BASEPATH
                        + f"/login?fail=Value {value} of key {key} is missing @"
                    )
                if "." not in value:
                    return redirect(
                        BASEPATH
                        + f"/login?fail=Value {value} of key {key} is missing ."
                    )

        # check authentication
        admin = Admin.query.filter_by(email=data["email"])[
            0
        ]  # should always only be one admin with this email

        # verify
        if Admin.verify_password(Admin, admin.hashed_password, data["password"]):
            session["admin_logged_in"] = True
            session["admin_user_id"] = admin.id
        else:
            session["admin_logged_in"] = False
            return redirect(BASEPATH + "/login?fail=Wrong password.")

        return redirect(BASEPATH)

    elif request.method == "GET":
        return render_template(
            "admin/login.html",
            name=config["settings"]["name"],
            fail=request.args.get("fail"),
            success=request.args.get("success"),
        )


@admin_routes.route(BASEPATH + "/logout")
def admin_logout():
    session.pop("admin_logged_in")

    return redirect(BASEPATH)
