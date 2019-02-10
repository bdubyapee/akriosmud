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
        self.title = ''
        self.skillpoints = 0
        self.seen_as = ''
        self.prompt = ''
        self.oocflags = {'afk': False,
                         'viewOLCdetails' : False,
                         'coding': False}
        self.oocflags_stored = {'newbie': 'true',
                                'mmchat': 'true',
                                'ooc': 'true',
                                'quote': 'true'}
        self.exp = {'combat': 0,
                    'explore': 0,
                    'profession': 0}
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
            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "name" : self.name,
                        "password" : self.password,
                        "capability" : self.capability,
                        "lasthost" : self.lasthost,
                        "lasttime" : self.lasttime,
                        "location" : self.location.vnum,
                        "long_description" : self.long_description,
                        "short_description" : self.short_description,
                        "race" : self.race.name,
                        "age" : self.age,
                        "gender" : self.gender,
                        "level" : self.level,
                        "alignment" : self.alignment,
                        "money" : self.money,
                        "height" : self.height,
                        "weight" : self.weight,
                        "maxhp" : self.maxhp,
                        "currenthp" :self.currenthp,
                        "maxmovement" : self.maxmovement,
                        "currentmovement" : self.currentmovement,
                        "maxwillpower" : self.maxwillpower,
                        "currentwillpower" : self.currentwillpower,
                        "totalmemoryslots" : self.totalmemoryslots,
                        "memorizedspells" : self.memorizedspells,
                        "hitroll" : self.hitroll,
                        "damroll" : self.damroll,
                        "wimpy" : self.wimpy,
                        "title" : self.title,
                        "guild" : self.guild,
                        "council" : self.council,
                        "family" : self.family,
                        "clan" : self.clan,
                        "deity" : self.deity,
                        "skillpoints" : self.skillpoints,
                        "seen_as" : self.seen_as,
                        "maximum_stat" : self.maximum_stat,
                        "current_stat" : self.current_stat,
                        "discipline" : self.discipline,
                        "exp" : self.exp,
                        "inventory" : self.inventory,
                        "worn" : self.worn,
                        "baceac" : self.baceac,
                        "currentac" : self.currentac,
                        "hunger" : self.hunger,
                        "thirst" : self.thirst,
                        "position" : self.position,
                        "aid" : self.aid,
                        "knownpeople" : self.knownpeople,
                        "prompt" : self.prompt,
                        "alias" : self.alias,
                        "oocflags_stored": self.oocflags_stored}

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        if self.json_version == 1:
            with open(f"{self.filename}", "w") as thefile:
                thefile.write(self.toJSON())


    @property
    def name_cap(self):
        return self.name.capitalize()

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


            
# This doesn't belong here, put somewhere else.
def statWords(self, statvalue = 55):
    if statvalue < 40:
        return "abismal"
    elif statvalue <= 44:
        return "terrible"
    elif statvalue <= 49:
        return "bad"
    elif statvalue <= 54:
        return "poor"
    elif statvalue <= 59:
        return "average"
    elif statvalue <= 64:
        return "fair"
    elif statvalue <= 69:
        return "good"
    elif statvalue <= 74:
        return "excellent"
    else:
        return "amazing"



