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
from components.core import is_integer
from components.update import check_for_new_releases
from sqlalchemy import or_

# blueprint init
admin_routes = Blueprint("admin_routes", __name__, template_folder="../templates")

# blueprint global variables
BASEPATH = "/admin"

# routes
@admin_routes.route(BASEPATH)
@admin_login_required
def index():
    tickets = Ticket.query.all()
    messages = Message.query.all()
    admins = Admin.query.all()

    return render_template(
        "admin/dashboard.html",
        num_tickets=len(tickets),
        num_messages=len(messages),
        num_admins=len(admins),
    )


@admin_routes.route(BASEPATH + "/system")
@admin_login_required
def system():
    status, new_release = check_for_new_releases()

    return render_template("admin/system.html", status=status, new_release=new_release,)


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

    return render_template("admin/tickets.html", tickets=tickets, view_msg=view_msg,)


@admin_routes.route(BASEPATH + "/tickets/<id>", methods=["POST", "GET"])
@admin_login_required
def view_ticket(id):
    template = "admin/view_ticket.html"

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

    # view ticket to admin if GET request
    if request.method == "GET":
        return render_template(
            template, ticket=ticket, messages=messages, admin_names=admin_names,
        )

    if request.method == "POST":
        data = request.form

        # admin is submitting a new message
        if data["request_type"] == "new_message":
            for key, value in data.items():
                if key != "message" and key != "request_type" and len(data) != 2:
                    return (
                        render_template(
                            template,
                            ticket=ticket,
                            messages=messages,
                            admin_names=admin_names,
                            fail="Invalid keys were sent.",
                        ),
                        400,
                    )

                if key == "message":
                    if len(value) > 500:
                        return (
                            render_template(
                                template,
                                ticket=ticket,
                                messages=messages,
                                admin_names=admin_names,
                                fail="Message too long.",
                            ),
                            400,
                        )

                    if len(value) < 3:
                        return (
                            render_template(
                                template,
                                ticket=ticket,
                                messages=messages,
                                admin_names=admin_names,
                                fail="Message too short.",
                            ),
                            400,
                        )

            # get ticket
            ticket = Ticket.query.get(int(id))

            try:
                message = Message(
                    message=data["message"],
                    sender_id=int(session.get("admin_user_id")),
                    ticket_id=int(id),
                )
            except Exception:
                return (
                    render_template(
                        "errors/custom.html",
                        title="400",
                        message="Ticket ID does not exist.",
                    ),
                    400,
                )

            # update status
            ticket.status = 2

            try:
                db.session.add(message)
                db.session.commit()
            except Exception:
                return (
                    render_template(
                        template,
                        ticket=ticket,
                        messages=messages,
                        admin_names=admin_names,
                        fail="Server error, could not create message.",
                    ),
                    500,
                )

            # message created successfully
            return render_template(
                template,
                ticket=ticket,
                messages=messages,
                admin_names=admin_names,
                success="Message sent!",
            )

        # admin is changing the status of the ticket
        if data["request_type"] == "status_update":
            for key, value in data.items():
                if key != "request_type" and key != "status" and len(data) != 2:
                    return render_template(
                        "errors/custom.html",
                        title="400",
                        message="Invalid keys were sent.",
                    )

                if key == "status":
                    if not is_integer(value):
                        return render_template(
                            "errors/custom.html",
                            title="400",
                            message="Value has to be integer.",
                        )

            # get ticket
            try:
                ticket = Ticket.query.get(int(id))
            except Exception:
                return (
                    render_template(
                        "errors/custom.html",
                        title="400",
                        message="Ticket ID does not exist.",
                    ),
                    400,
                )

            ticket.status = int(data["status"])

            try:
                db.session.commit()
            except Exception:
                return (
                    render_template(
                        "admin/view_ticket.html",
                        ticket=ticket,
                        messages=messages,
                        admin_names=admin_names,
                        fail="Unable to update status.",
                    ),
                    500,
                )

            # status updated successfully
            return render_template(
                "admin/view_ticket.html",
                ticket=ticket,
                messages=messages,
                admin_names=admin_names,
                success="Status has been updated.",
            )

        # invalid request
        return (
            render_template(
                template,
                ticket=ticket,
                messages=messages,
                admin_names=admin_names,
                fail="Invalid request type",
            ),
            400,
        )


@admin_routes.route(BASEPATH + "/login", methods=["POST", "GET"])
def admin_login():
    template = "admin/login.html"

    if request.method == "POST":
        data = request.form

        # validation check
        for key, value in data.items():
            if key != "email" and key != "password":
                return (
                    render_template(template, fail="Invalid keys were sent.",),
                    400,
                )

            if len(value) < 3:
                return (
                    render_template(template, fail=f"{key} is too short.",),
                    400,
                )

            if key == "email":
                if len(value) > 50:
                    return (
                        render_template(template, fail=f"{key} is too long.",),
                        400,
                    )
                if "@" not in value:
                    return (
                        render_template(template, fail=f"Email is missing '@'.",),
                        400,
                    )
                if "." not in value:
                    return (
                        render_template(template, fail=f"Email is missing '.'",),
                        400,
                    )

        # check authentication
        try:
            admin = Admin.query.filter_by(email=data["email"])[
                0
            ]  # should always only be one admin with this email
        except Exception:
            return render_template(
                template, fail="Account does not exist or wrong password.",
            )

        # verify
        if Admin.verify_password(Admin, admin.hashed_password, data["password"]):
            session["admin_logged_in"] = True
            session["admin_user_id"] = admin.id
        else:
            session["admin_logged_in"] = False
            return (
                render_template(
                    template, fail="Account does not exist or wrong password.",
                ),
                400,
            )

        return redirect(BASEPATH)

    elif request.method == "GET":
        return render_template(template)


@admin_routes.route(BASEPATH + "/logout")
def admin_logout():
    session.pop("admin_logged_in")

    return redirect(BASEPATH)


@admin_routes.route(BASEPATH + "/users")
@admin_login_required
def users():
    template = "admin/users.html"
    admins = Admin.query.with_entities(
        Admin.id, Admin.name, Admin.email, Admin.time_created
    )

    return render_template(template, admins=admins)
