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
import uuid

import area
import livingthing
import olc
import room
import event
import races


WRITE_NEW_FILE_VERSION = False


class Mobile(livingthing.LivingThing, olc.Editable):
    CLASS_NAME = "__Mobile__"
    FILE_VERSION = 1

    def __init__(self, area, data=None, index=True):
        super().__init__()
        self.json_version = Mobile.FILE_VERSION
        self.json_class_name = Mobile.CLASS_NAME
        self.logpath = ''
        self.capability = ['mobile']
        self.vnum = 0
        self.keywords = []
        self.area = area
        self.index = index
        self.events = event.Queue(self, "mobile")
        self.commands = {"vnum": ("integer", None),
                         "name": ("string", None)}
        if data is not None:
            self.load(data)

    def populate_index(self):
        self.area.mobilelist_index.append(self)
        self.area.mobilelist_by_vnum_index[self.vnum] = self

    def populate_real(self):
        self.area.mobilelist.append(self)
        self.area.mobilelist_by_vnum[self.vnum] = self

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        self.location = None
        self.race = races.racebyname(self.race)
        
        if not self.equipped:
            self.equipped = {k: None for k in self.race.wearlocations}

        if self.index:
            self.populate_index()
        else:
            self.populate_real()

    def to_json(self):
        if self.json_version == 1:
            jsonable = self.to_json_base()
            mobile_json = {"json_version": self.json_version,
                           "json_class_name": self.json_class_name,
                           "keywords": self.keywords,
                           "vnum": self.vnum}

            jsonable.update(mobile_json)

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def create_instance(self, location=None):
        '''
            This creates a 'real' in game version of a mobile. We expect a location to be
            provided in which to place the mobile.  If the location passed in is an int type
            and if that int is a valid room vnum, put the mobile there.  If not we assume,
            at this time, that it is a room object and we place it there.
        '''
        if location is None:
            comm.wiznet(f"Cannot load Mobile to None Location.")
            return
        elif type(location) is int and location in self.area.roomlist:
            newroom = self.area.room_by_vnum(location)
        else:
            newroom = location

        new_mob = Mobile(self.area, self.toJSON(), index=False)
        new_mob.aid = str(uuid.uuid4())

        new_mob.move(newroom)

    def write(self, args):
        print(f"Received mobile command write of: {args}")

