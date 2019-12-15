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

import string
import json
import random


def random_string(length=10):
    """Generate a random string of fixed length"""

    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for i in range(length)
    )


def is_integer(string):
    try:
        int(string)
    except Exception:
        return False

    return True


def read_configuration():
    """Returns JSON object with configuration"""

    with open("config.json") as f:
        config = json.load(f)

    return config


def is_valid_input(variable, allow_space=True, swedish=True, allow_newline=True):
    """Returns boolean whether variable is valid input or not"""

    ILLEGAL_CHARACTERS = ["<", ">", ";"]
    ALLOWED_CHARACTERS = list(string.printable)

    if not allow_space:
        ALLOWED_CHARACTERS.remove(" ")

    if not allow_newline:
        ALLOWED_CHARACTERS.remove("\n")

    if swedish:
        ALLOWED_CHARACTERS.extend(["å", "ä", "ö", "Å", "Ä", "Ö"])

    if any(x in variable for x in ILLEGAL_CHARACTERS):
        return False

    if any(x not in ALLOWED_CHARACTERS for x in variable):
        return False

    return True
