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
from components.tools import random_string

class TicketsTable:
    def __init__(self):
        '''Initializes Tickets table'''

        self.name = 'Tickets'

        result = sql_query(f'''CREATE TABLE {self.name} (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            client_key VARCHAR(15),
            status int NOT NULL,
            creation_date DATETIME
        ); ''')

        if result["status"]:
            return None

        if f'''Table '{self.name}' already exists''' in result["result"]:
            return None

        raise Exception(f'unable to create table {self.name}, error message {result["result"]}')

    def fetch_all(self):
        '''Returns list of all Tickets'''

        query = sql_query(f'SELECT * FROM {self.name}')

        if query["status"]:
            return query["result"]

        raise Exception(f'unable to get {self.name}, error {query["result"]}')

    def new(self, name, email, status=0):
        query = sql_query(f'''INSERT INTO {self.name} (name, email, client_key, status, creation_date)
            VALUES ("{name}", "{email}", "{random_string(length = 15)}"," {status}, CURRENT_TIMESTAMP())
        ''')

        if query["status"]:
            return query["result"]

        raise Exception(f'unable to create new {self.name}, error {query["result"]}')

    def get_id(self, id):
        query = sql_query(f'''SELECT * FROM {self.name} WHERE id={id}''')

        if query["status"]:
            return query["result"]
        
        raise Exception(f'unable to fetch obj using id from {self.name}, error {query["result"]}')