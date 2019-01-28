#! usr/bin/env python
# Project: Akrios
# Filename: room.py
# 
# File Description: Module dealing with rooms specifically.
# 
# By: Jubelo

from collections import namedtuple
import json
import os
import glob

import olc
import area
import event
import exits


# Define some named tuples for varios room values.

# Flags specific to one room.
RoomFlag = namedtuple("RoomFlag", "name")

room_flags = {"none": RoomFlag("none"),
              "fire": RoomFlag("fire"),
              "deadzone" : RoomFlag("deadzone"),
              "dark" : RoomFlag("dark"),
              "sanctuary" : RoomFlag("sanctuary"),
              "peace" : RoomFlag("peace"),
              "inn" : RoomFlag("inn"),
              "nomagic" : RoomFlag("nomagic")}


# Sector Types that can be set per room.
SectorType = namedtuple("SectorType", "name")

sector_types = {"inside": SectorType("inside"),
                "city": SectorType("city"),
                "field": SectorType("field"),
                "forest": SectorType("forest"),
                "hills": SectorType("hills"),
                "mountain": SectorType("mountain"),
                "water": SectorType("water"),
                "deepwater": SectorType("deepwater"),
                "air": SectorType("air"),
                "desert": SectorType("desert"),
                "jungle": SectorType("jungle"),
                "swamp": SectorType("swamp"),
                "cave": SectorType("cave"),
                "underwater": SectorType("underwater")}


# Property value for rooms.
PropertyValue = namedtuple("PropertyValue", "name")

property_values = {"very poor": PropertyValue("very poor"),
                   "poor": PropertyValue("poor"),
                   "moderate": PropertyValue("moderate"),
                   "upper moderate": PropertyValue("upper moderate"),
                   "rich": PropertyValue("rich"),
                   "very rich": PropertyValue("very rich")}



class oneRoom(olc.Editable):
    CLASS_NAME = "__oneRoom__"
    FILE_VERSION = 1

    def __init__(self, area, data=None, vnum=None):
        super().__init__()

        self.json_version = oneRoom.FILE_VERSION
        self.json_class_name = oneRoom.CLASS_NAME
        self.area = area
        self.builder = None
        if vnum != None:
            self.vnum = vnum
        else:
            self.vnum = 0
        self.name = "Blank Room"
        self.description = ""
        self.propertyvalue = ""
        self.flags = []
        self.sectortype = []
        self.extradescriptions = {}
        self.exits = {}
        self.contents = []
        self.events = event.Queue(self, "room")
        event.init_events_room(self)
        self.commands = {"builder": ("string", None),
                         "vnum": ("integer", None),
                         "name": ("string", None),
                         "description": ("description", None),
                         "propertyvalue": ("string", property_values),
                         "flags": ("list", room_flags),
                         "sectortype": ("list", sector_types),
                         "extradescriptions": ("dict", (None, None))}
        if data is not None:
            self.load(data)

    def toJSON(self):
        if self.json_version == 1:
            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "vnum" : self.vnum,
                        "name" : self.name,
                        "description" : self.description,
                        "flags" : self.flags,
                        "sectortype" : self.sectortype,
                        "propertyvalue" : self.propertyvalue,
                        "extradescriptions" : self.extradescriptions}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        self.area.roomlist[self.vnum] = self
        area.roomlist[self.vnum] = self

    def display(self):
        return(f"{{BArea{{x: {self.area.name}\n"
               f"{{BBuilder{{x: {self.builder.name}\n"
               f"{{BVnum{{x: {self.vnum}\n"
               f"{{BName{{x: {self.name}\n"
               f"{{BProperty Value{{x: {self.propertyvalue}\n"
               f"   {{y{', '.join(property_values)}{{x\n"
               f"{{BFlags{{x: {self.flags}\n"
               f"   {{y{', '.join(room_flags)}\n"
               f"{{BSector Type{{x: {self.sectortype}\n"
               f"   {{y{', '.join(sector_types)}\n"
               f"{{BExtra Desc{{x: {self.extradescriptions}\n"
               f"{{BExits{{x: {', '.join(self.exits)}\n"
               f"{{BDescription{{x: {self.description[:180]}{{x\n")


