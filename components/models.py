
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

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import hashlib, binascii, os

db = SQLAlchemy()

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=False, nullable=False)
    client_key = db.Column(db.String(15), unique=False, nullable=False)
    status = db.Column(db.Integer, unique=False, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    messages = db.relationship('Message', backref='ticket', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), unique=False, nullable=False)
    sender_id = db.Column(db.Integer, unique=False, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), unique=True, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def hash_password(password):
        """Hash a password for storing"""

        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                    salt, 100000)
        
        pwdhash = binascii.hexlify(pwdhash)
        
        return (salt + pwdhash).decode('ascii')

    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                        provided_password.encode('utf-8'), 
                                        salt.encode('ascii'), 
                                        100000)
        
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        
        return pwdhash == stored_password
