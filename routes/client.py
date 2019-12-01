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
from components.tools import is_integer, random_string, read_configuration

# blueprint init
client_routes = Blueprint("client_routes", __name__, template_folder="../templates")

# blueprint global variables
config = read_configuration()

# routes
@client_routes.route("/")
def index():
    return render_template(
        "client/index.html",
        name=config["settings"]["name"],
        admin_status=session.get("admin_logged_in"),
    )


@client_routes.route("/submit", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        data = request.form

        for key, value in data.items():
            if key != "name" and key != "email" and key != "message":
                return redirect("/submit?fail=Invalid keys were sent.")

            if len(value) < 3:
                return redirect(f"/submit?fail={key} is too short.")

            if key == "name":
                if len(value) > 50:
                    return redirect(
                        f"/submit?fail=Value {value} of key {key} is too long."
                    )

            if key == "email":
                if len(value) > 50:
                    return redirect(
                        f"/submit?fail=Value {value} of key {key} is too long."
                    )
                if "@" not in value:
                    return redirect(
                        f"/submit?fail=Value {value} of key {key} is missing @."
                    )
                if "." not in value:
                    return redirect(
                        f"/submit?fail=Value {value} of key {key} is missing ."
                    )

            if key == "message":
                if len(value) > 500:
                    return redirect(
                        f"/submit?fail=Value {value} of key {key} is too long."
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
            return redirect("/submit?fail=Internal server error occured.")

        # commit
        try:
            db.session.commit()
        except Exception as err:
            return redirect("/submit?fail=Internal server error occured.")

        # trigger update
        ticket = Ticket.query.get(ticket.id)
        ticket.status = 1
        db.session.commit()

        ticket = Ticket.query.get(ticket.id)
        ticket.status = 0
        db.session.commit()

        return redirect(f"/ticket?id={ticket.id}&key={ticket.client_key}")

    if request.method == "GET":
        return render_template(
            "client/submit.html",
            name=config["settings"]["name"],
            admin_status=session.get("admin_logged_in"),
            fail=request.args.get("fail"),
            success=request.args.get("success"),
        )


@client_routes.route("/ticket")
def ticket():
    data = request.args

    if not data or len(data) < 2:
        return (
            render_template(
                "errors/custom.html", title="400", message="Missing arguments."
            ),
            400,
        )

    for key, value in data.items():
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
    ticket = Ticket.query.get(data["id"])

    if ticket.client_key != data["key"]:
        return (
            render_template(
                "errors/custom.html", title="400", message="Secret key is invalid."
            ),
            400,
        )

    messages = Message.query.filter_by(ticket_id=data["id"]).order_by(Message.id.desc())

    # build dict with admins
    admins = Admin.query.all()

    admin_names = {}

    for admin in admins:
        admin_names[admin.id] = admin.name

    return render_template(
        "client/ticket.html",
        name=config["settings"]["name"],
        admin_status=session.get("admin_logged_in"),
        ticket=ticket,
        messages=messages,
        admin_names=admin_names,
        fail=request.args.get("fail"),
        success=request.args.get("success"),
    )


@client_routes.route("/submitmessage", methods=["POST"])
def submitmessage():
    data = request.form

    if not data or len(data) < 3:
        return redirect(
            f"/ticket?id={data['ticket_id']}&key={data['client_key']}&fail=Missing arguments."
        )

    for key, value in data.items():
        if key != "message" and key != "ticket_id" and key != "client_key":
            return redirect(
                f"/ticket?id={data['ticket_id']}&key={data['client_key']}&fail=Invalid keys sent."
            )

        if key == "ticket_id":
            if not is_integer(value):
                return (
                    render_template(
                        "errors/custom.html", title="400", message="id must be integer"
                    ),
                    400,
                )

        if key == "message":
            if len(value) > 500:
                return redirect(
                    f"/ticket?id={data['ticket_id']}&key={data['client_key']}&fail=Value {value} of key {key} is too long."
                )

            if len(value) < 3:
                return redirect(
                    f"/ticket?id={data['ticket_id']}&key={data['client_key']}&fail=Value {value} of key {key} is too short."
                )

    # check if secret_key is correct
    ticket = Ticket.query.get(data["ticket_id"])

    if ticket.client_key != data["client_key"]:
        return (
            render_template(
                "errors/custom.html", title="400", message="Invalid secret key."
            ),
            400,
        )

    try:
        message = Message(
            message=data["message"], sender_id=0, ticket_id=int(data["ticket_id"])
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

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        return (
            render_template(
                "errors/custom.html", title="500", message="Unable to create message."
            ),
            500,
        )

    return redirect(
        f"/ticket?id={ticket.id}&key={ticket.client_key}&success=Message sent!"
    )
