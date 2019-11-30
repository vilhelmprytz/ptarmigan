#!/usr/bin/env python3

from app import db, app
from components.models import Admin

new_name = input("Enter name: ")
new_email = input("Enter email: ")
new_password = input("Enter password: ")

admin = Admin(
    name=new_name,
    email=new_email,
    hashed_password=Admin.hash_password(Admin, new_password),
)

with app.app_context():
    db.session.add(admin)
    db.session.commit()
