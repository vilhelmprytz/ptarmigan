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
from components.core import (
    is_integer,
    random_string,
    is_valid_input,
)

# blueprint init
client_routes = Blueprint("client_routes", __name__, template_folder="../templates")

# blueprint global variables

# routes
@client_routes.route("/")
def index():
    return render_template(
        "client/index.html", admin_status=session.get("admin_logged_in"),
    )


@client_routes.route("/submit", methods=["POST", "GET"])
def submit():
    template = "client/submit.html"

    if request.method == "POST":
        data = request.form

        for key, value in data.items():
            if key != "name" and key != "email" and key != "message" and len(data) != 3:
                return (
                    render_template(
                        template,
                        admin_status=session.get("admin_logged_in"),
                        fail="Invalid keys were sent.",
                    ),
                    400,
                )

            if len(value) < 3:
                return (
                    render_template(
                        template,
                        admin_status=session.get("admin_logged_in"),
                        fail=f"Value of {key} is too short.",
                        prefill_values={
                            "name": data["name"],
                            "email": data["email"],
                            "message": data["message"],
                        },
                    ),
                    400,
                )

            if key == "name":
                if len(value) > 50:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            fail=f"Name can max be 50 characters long.",
                            prefill_values={
                                "name": data["name"],
                                "email": data["email"],
                                "message": data["message"],
                            },
                        ),
                        400,
                    )

            if key == "email":
                if len(value) > 50:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            fail=f"Email can max be 50 characters long.",
                            prefill_values={
                                "name": data["name"],
                                "email": data["email"],
                                "message": data["message"],
                            },
                        ),
                        400,
                    )
                if "@" not in value:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            fail=f"Missing '@' in email.",
                        ),
                        400,
                    )
                if "." not in value:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            fail=f"Email doesn't appear to be a valid email address.",
                            prefill_values={
                                "name": data["name"],
                                "email": data["email"],
                                "message": data["message"],
                            },
                        ),
                        400,
                    )
                if not is_valid_input(
                    value, allow_space=False, swedish=False, allow_newline=False
                ):
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            fail=f"Email contains illegal characters (no space allowed).",
                            prefill_values={
                                "name": data["name"],
                                "email": data["email"],
                                "message": data["message"],
                            },
                        ),
                        400,
                    )

            if key == "message":
                if len(value) > 500:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            fail=f"Message can max be 500 characters long.",
                            prefill_values={
                                "name": data["name"],
                                "email": data["email"],
                                "message": data["message"],
                            },
                        ),
                        400,
                    )

            # check if valid
            if not is_valid_input(key) or not is_valid_input(value):
                return (
                    render_template(
                        template,
                        admin_status=session.get("admin_logged_in"),
                        fail=f"Data contains illegal characters.",
                        prefill_values={
                            "name": data["name"],
                            "email": data["email"],
                            "message": data["message"],
                        },
                    ),
                    400,
                )

        # create objects
        try:
            ticket = Ticket(
                name=data["name"],
                email=data["email"],
                client_key=random_string(length=15),
                status=0,
            )
            db.session.add(ticket)
            db.session.flush()
            message = Message(
                message=data["message"], sender_id=0, ticket_id=ticket.id
            )  # sender_id=0 will always be client in conversation
            db.session.add(message)
        except Exception as err:
            # `err` should be logged to logger when logger is implemented
            print(str(err))
            return (
                render_template(
                    template,
                    admin_status=session.get("admin_logged_in"),
                    fail=f"Internal server error occured.",
                    prefill_values={
                        "name": data["name"],
                        "email": data["email"],
                        "message": data["message"],
                    },
                ),
                500,
            )

        # commit
        try:
            db.session.commit()
        except Exception as err:
            # `err` should be logged to logger when logger is implemented
            print(str(err))
            return (
                render_template(
                    template,
                    admin_status=session.get("admin_logged_in"),
                    fail=f"Internal server error occured.",
                    prefill_values={
                        "name": data["name"],
                        "email": data["email"],
                        "message": data["message"],
                    },
                ),
                500,
            )

        # trigger update
        ticket = Ticket.query.get(ticket.id)
        ticket.status = 1
        db.session.commit()

        ticket = Ticket.query.get(ticket.id)
        ticket.status = 0
        db.session.commit()

        # success
        return redirect(f"/ticket?id={ticket.id}&key={ticket.client_key}")

    if request.method == "GET":
        return render_template(template, admin_status=session.get("admin_logged_in"),)


@client_routes.route("/ticket", methods=["POST", "GET"])
def ticket():
    template = "client/ticket.html"
    url_data = request.args
    data = request.form

    if not url_data or len(url_data) < 2:
        return (
            render_template(
                "errors/custom.html", title="400", message="Missing arguments."
            ),
            400,
        )

    for key, value in url_data.items():
        if key != "id" and key != "key" and key != "success" and key != "fail":
            return (
                render_template(
                    "errors/custom.html", title="400", message="Invalid keys were sent."
                ),
                400,
            )

        if key == "id":
            if not is_integer(value):
                return (
                    render_template(
                        "errors/custom.html", title="400", message="Id must be integer."
                    ),
                    400,
                )

        if key == "key":
            if len(value) != 15:
                return (
                    render_template(
                        "errors/custom.html",
                        title="400",
                        message="Secret key is invalid length.",
                    ),
                    400,
                )

    # check if secret_key is correct
    ticket = Ticket.query.get(url_data["id"])

    if ticket.client_key != url_data["key"]:
        return (
            render_template(
                "errors/custom.html", title="400", message="Secret key is invalid."
            ),
            400,
        )

    messages = Message.query.filter_by(ticket_id=url_data["id"]).order_by(
        Message.id.desc()
    )

    # build dict with admins
    admins = Admin.query.all()

    admin_names = {}

    for admin in admins:
        admin_names[admin.id] = admin.name

    # if user is trying to view ticket
    if request.method == "GET":
        return render_template(
            template,
            admin_status=session.get("admin_logged_in"),
            ticket=ticket,
            messages=messages,
            admin_names=admin_names,
        )

    # if user is trying to submit a new message
    if request.method == "POST":
        if not data or len(data) != 1:
            return (
                render_template(
                    template,
                    admin_status=session.get("admin_logged_in"),
                    ticket=ticket,
                    messages=messages,
                    admin_names=admin_names,
                    fail="Missing arguments/invalid arguments.",
                ),
                400,
            )

        for key, value in data.items():
            if key != "message":
                return (
                    render_template(
                        template,
                        admin_status=session.get("admin_logged_in"),
                        ticket=ticket,
                        messages=messages,
                        admin_names=admin_names,
                        fail="Invalid data sent.",
                    ),
                    400,
                )

            if key == "message":
                if len(value) > 500:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            ticket=ticket,
                            messages=messages,
                            admin_names=admin_names,
                            fail="Message is too long, maximum is 500 characters.",
                        ),
                        400,
                    )

                if len(value) < 3:
                    return (
                        render_template(
                            template,
                            admin_status=session.get("admin_logged_in"),
                            ticket=ticket,
                            messages=messages,
                            admin_names=admin_names,
                            fail="Message is too short, minimum is 3 characters.",
                        ),
                        400,
                    )

        # get ticket info
        try:
            message = Message(
                message=data["message"], sender_id=0, ticket_id=int(url_data["id"])
            )
        except Exception:
            return (
                render_template(
                    "errors/custom.html", title="400", message="Ticket does not exist."
                ),
                400,
            )

        # update status
        ticket.status = 1

        # create message
        try:
            db.session.add(message)
            db.session.commit()
        except Exception:
            return (
                render_template(
                    template,
                    admin_status=session.get("admin_logged_in"),
                    ticket=ticket,
                    messages=messages,
                    admin_names=admin_names,
                    fail="Internal server error occured while creating message.",
                ),
                500,
            )

        # successfully created message
        return (
            render_template(
                template,
                admin_status=session.get("admin_logged_in"),
                ticket=ticket,
                messages=messages,
                admin_names=admin_names,
                success="Message has been sent!",
            ),
            500,
        )
