#! usr/bin/env python
# Project: Akrios
# Filename: player.py
# 
# File Description: The player module.
# 
# By: Jubelo

from collections import namedtuple
import importlib
import json
import os
import time

import area
import livingthing
import room
import event
import races


WRITE_NEW_FILE_VERSION = False

playerlist = []
playerlist_by_name = {}
playerlist_by_aid = {}


class Player(livingthing.LivingThing):
    CLASS_NAME = "__Player__"
    FILE_VERSION = 1

    def __init__(self, path=None):
        super().__init__()
        self.filename = path
        self.json_version = Player.FILE_VERSION
        self.json_class_name = Player.CLASS_NAME
        self.logpath = ''
        self.capability = ['player']
        self.password = ''
        self.lasthost = ''
        self.lasttime = ''
        self.oocflags = {'afk': False,
                         'viewOLCdetails' : False,
                         'coding': False}
        self.oocflags_stored = {'newbie': 'true',
                                'mmchat': 'true',
                                'ooc': 'true',
                                'quote': 'true'}
        self.events = event.Queue(self, "player")
        self.sock = None
        if self.filename != None:
            self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as thefile:
                player_file_dict = json.loads(thefile.read())
                for eachkey, eachvalue in player_file_dict.items():
                    setattr(self, eachkey, eachvalue)
            self.location = area.roomByVnum(self.location)
            self.move(self.location)
            self.race = races.racebyname(self.race)

    def toJSON(self):
        if self.json_version == 1:
            jsonable = self.toJSON_base()
            player_json = {"json_version": self.json_version,
                           "json_class_name": self.json_class_name,
                           "password": self.password,
                           "lasthost": self.lasthost,
                           "lasttime": self.lasttime,
                           "oocflags_stored": self.oocflags_stored}

            jsonable.update(player_json)

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        if self.json_version == 1:
            with open(f"{self.filename}", "w") as thefile:
                thefile.write(self.toJSON())


    @property
    def is_building(self):
        if hasattr(self, "building"):
            return True
        else:
            return False

    @property
    def is_editing(self):
        if hasattr(self, "editing"):
            return True
        else:
            return False


