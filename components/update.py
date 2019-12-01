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

import requests


def check_for_new_releases():
    r = requests.get("https://api.github.com/repos/VilhelmPrytz/ptarmigan/tags")

    if r.status_code == requests.codes.ok:
        try:
            latest_release = r.json()[0]["name"]
        except Exception:
            return False, "Unable to retrieve latest version."
    else:
        return False, "Unable to retrieve latest version"

    return True, latest_release
