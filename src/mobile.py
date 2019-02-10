#! usr/bin/env python
# Project: Akrios
# Filename: mobile.py
# 
# File Description: The mobile module.
# 
# By: Jubelo

from collections import namedtuple
import importlib
import json
import os
import time

import area
import livingthing
import olc
import room
import event
import races


WRITE_NEW_FILE_VERSION = False


# This warrants some explanation.  The _index lists or dicts below are the in-memory
# version of the mobile.  We will load all Mobiles for an area into this list.
# During the final loading phase for an area we will go through all of the 
# reset information and instanciate in-game versions of the Mobiles.

mobilelist_index = []
mobilelist = []
mobilelist_by_vnum_index = {}
mobilelist_by_vnum = {}
mobilelist_by_name_index = {}
mobilelist_by_name = {}
mobilelist_by_aid_index = {}
mobilelist_by_aid = {}


class Mobile(livingthing.LivingThing, olc.Editable):
    CLASS_NAME = "__Mobile__"
    FILE_VERSION = 1

    def __init__(self, path=None):
        super().__init__()
        self.filename = path
        self.json_version = Mobile.FILE_VERSION
        self.json_class_name = Mobile.CLASS_NAME
        self.logpath = ''
        self.capability = ['mobile']
        self.title = ''
        self.seen_as = ''
        self.prompt = ''
        self.vnum = 0
        self.events = event.Queue(self, "mobile")
        self.commands = {"vnum": ("integer", None),
                         "name": ("string", None)}
        if self.filename != None:
            self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as thefile:
                mobile_file_dict = json.loads(thefile.read())
                for eachkey, eachvalue in mobile_file_dict.items():
                    setattr(self, eachkey, eachvalue)
            self.race = races.racebyname(self.race)

            mobilelist_index.append(self)
            mobilelist_by_vnum[self.vnum] = self
            mobilelist_by_name[self.name] = self
            mobilelist_by_aid[self.aid] = self

    def toJSON(self):
        if self.json_version == 1:
            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "name" : self.name,
                        "capability" : self.capability,
                        "vnum" : self.vnum,
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
                        "alias" : self.alias}

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        if self.json_version == 1:
            with open(f"{self.filename}", "w") as thefile:
                thefile.write(self.toJSON())


