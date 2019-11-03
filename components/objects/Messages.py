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

class MessagesTable:
    def __init__(self):
        '''Initalizes Messages table'''

        self.name = 'Messages'

        result = sql_query('''CREATE TABLE Messages (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            ticket_id INT,
            message VARCHAR(255),
            sender_id INT,
            date DATETIME
        ); ''')

        if result["status"]:
            return None

        if f'''Table '{self.name}' already exists''' in result["result"]:
            return None

        raise Exception(f'unable to create table {self.name}, error message {result["result"]}')

    def fetch_all(self):
        '''Returns list of all Messages'''

        query = sql_query(f'SELECT * FROM {self.name}')

        if query["status"]:
            return query["result"]

        raise Exception(f'unable to get {self.name}, error {query["result"]}')

    def new(self, ticket_id, message, sender_id):
        query = sql_query(f'''INSERT INTO {self.name} (ticket_id, message, sender_id, date)
            VALUES ({ticket_id}, "{message}", "{sender_id}", CURRENT_TIMESTAMP())
        ''')

        if query["status"]:
            return query["result"]

        raise Exception(f'unable to create new {self.name}, error {query["result"]}')

    def get_id(self, id):
        query = sql_query(f'''SELECT * FROM {self.name} WHERE id={id}''')

        if query["status"]:
            return query["result"]
        
        raise Exception(f'unable to fetch obj using id from {self.name}, error {query["result"]}')

    def get_ticket_id(self, ticket_id):
        query = sql_query(f'''SELECT * FROM {self.name} WHERE ticket_id={ticket_id}''')

        if query["status"]:
            return query["result"]
        
        raise Exception(f'unable to fetch objs using ticket_id from {self.name}, error {query["result"]}')