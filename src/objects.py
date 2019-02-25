#! usr/bin/env python
# Project: Akrios
# Filename: objects.py
# 
# File Description: The mobile module.
# 
# By: Jubelo

from collections import namedtuple
import json
import os
import time
import uuid

import area
import atomic
import olc
import room
import event
import races


WRITE_NEW_FILE_VERSION = False


# This warrants some explanation.  The _index lists or dicts below are the in-memory
# version of the object.  We will load all Objects for an area into this list.
# During the final loading phase for an area we will go through all of the 
# reset information and instanciate in-game versions of the Objects.

objectlist_index = []
objectlist = []
objectlist_by_vnum_index = {}


class Object(atomic.Atomic, olc.Editable):
    CLASS_NAME = "__Object__"
    FILE_VERSION = 1

    def __init__(self, area, data=None, load_type=None):
        super().__init__()
        self.json_version = Object.FILE_VERSION
        self.json_class_name = Object.CLASS_NAME
        self.aid = ''
        self.capability = ['object']
        self.vnum = 0
        self.location = None
        self.name = ''
        self.short_description = ''
        self.long_description = ''
        self.keywords = []
        self.contents = {}
        self.area = area
        self.events = event.Queue(self, "object")
        self.commands = {"vnum": ("integer", None),
                         "short_description": ("string", None),
                         "long_description": ("string", None),
                         "name": ("sting", None),
                         "keywords": ("list", None)}

        if data is not None and load_type is not None:
            self.load(data, load_type)

    def populate_index(self):
        objectlist_index.append(self)
        objectlist_by_vnum_index[self.vnum] = self
        self.area.objectlist_index.append(self)
        self.area.objectlist_by_vnum_index[self.vnum] = self

    def populate_instance(self):
        objectlist.append(self)
        self.area.objectlist.append(self)

    def load(self, data, load_type):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        if load_type == "index":
            self.populate_index()
            return

        if load_type == "instance":
            self.populate_instance()
            return
            
    def toJSON(self):
        if self.json_version == 1:
            jsonable = {"json_version": self.json_version,
                        "json_class_name": self.json_class_name,
                        "aid": self.aid or str(uuid.uuid4()),
                        "name": self.name,
                        "short_description": self.short_description,
                        "long_description": self.long_description,
                        "keywords": self.keywords,
                        "contents": self.contents,
                        "vnum": self.vnum}

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def create_instance(self, location=None):
        '''
            This creates a 'real' in game version of an object. We expect a location to be
            provided in which to place the object.  If the location passed in is an int type
            and if that int is a valid room vnum, put the object there.  If not we assume,
            at this time, that it is a room object and we place it there.
        '''
        if location is None:
            comm.wiznet(f"Cannot load Object to None Location.")
            return
        elif type(location) is int and location in area.roomlist:
            newroom = area.roomByVnum(location)
        else:
            newroom = location

        new_obj = Object(self.area, self.toJSON(), load_type="instance")
        new_obj.aid = str(uuid.uuid4())

        new_obj.move(newroom)

    def write(self, args):
        print(f"Received object command write of: {args}")

