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

from components.sql import sql_query
import hashlib, binascii, os

class AdminsTable:
    def __init__(self):
        '''Initalizes Admins table'''

        self.name = 'Admins'

        result = sql_query('''CREATE TABLE Admins (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            hashed_password VARCHAR(255),
            creation_date DATETIME
        ); ''')

        if result["status"]:
            return None

        if f'''Table '{self.name}' already exists''' in result["result"]:
            return None

        raise Exception(f'unable to create table {self.name}, error message {result["result"]}')

    def fetch_all(self):
        '''Returns list of all Admins'''

        query = sql_query(f'SELECT * FROM {self.name}')

        if query["status"]:
            return query["result"]

        raise Exception(f'unable to get {self.name}, error {query["result"]}')

    def hash_password(self, password):
        """Hash a password for storing"""

        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                    salt, 100000)
        
        pwdhash = binascii.hexlify(pwdhash)
        
        return (salt + pwdhash).decode('ascii')

    def verify_password(self, stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                        provided_password.encode('utf-8'), 
                                        salt.encode('ascii'), 
                                        100000)
        
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        
        return pwdhash == stored_password

    def new(self, name, email, raw_password):
        hashed_password = self.hash_password(raw_password)

        query = sql_query(f'''INSERT INTO {self.name} (name, email, hashed_password, creation_date)
            VALUES ("{name}", "{email}", "{hashed_password}", CURRENT_TIMESTAMP())
        ''')

        if query["status"]:
            return query["result"]

        raise Exception(f'unable to create new {self.name}, error {query["result"]}')

    def get_id(self, id):
        query = sql_query(f'''SELECT * FROM {self.name} WHERE id={id}''')

        if query["status"]:
            return query["result"]
        
        raise Exception(f'unable to fetch obj using id from {self.name}, error {query["result"]}')