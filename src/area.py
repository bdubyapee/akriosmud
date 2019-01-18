#! usr/bin/env python
# Project: Akrios
# Filename: area.py
# 
# File Description: File dealing with areas
# 
# By: Jubelo

from collections import namedtuple
import os
import json
import re
import glob

import comm
import olc
import room
import event
import exits
import world


arealist = []
roomlist = {}
mobilelist = {}
objectlist = {}


# Define some named tuples of various Area values.
Plane = namedtuple("Planes", "name")

planes = {"material": Plane("material"),
          "ethereal": Plane("ethereal")}


Difficulty = namedtuple("Difficulty", "name")

difficulty = {"all": Difficulty("all"),
              "very easy": Difficulty("very easy"),
              "easy": Difficulty("easy"),
              "moderate": Difficulty("moderate"),
              "hard": Difficulty("hard"),
              "very hard": Difficulty("very hard"),
              "extreme": Difficulty("extreme")}


def init():
    for each_area_directory in glob.glob(os.path.join(world.areaDir, '*')):
        thefile = glob.glob(os.path.join(each_area_directory, '*.json'))
        oneArea(each_area_directory, thefile[0])

def roomByVnum(vnum):
    if vnum in roomlist.keys():
        return roomlist[vnum]
    else:
        return False



class oneArea(olc.Editable):
    CLASS_NAME = "__oneArea__"
    FILE_VERSION = 1

    def __init__(self, fpath, path):
        super().__init__()

        self.json_version = oneArea.FILE_VERSION
        self.json_class_name = oneArea.CLASS_NAME
        self.folder_path = fpath
        self.area_path = path
        self.name = ''
        self.author = ''
        self.plane = ''
        self.hometown = ''
        self.difficulty = ''
        self.alignment = ''
        self.locationx = 0
        self.locationy = 0
        self.vnumlow = -1
        self.vnumhigh = -1
        self.roomlist = {}
        self.moblist = {}
        self.objectlist = {}
        self.mobindexlist = {}
        self.objectindexlist = {}
        self.resetlist = []
        self.shoplist = []
        self.playerlist = []
        self.events = event.Queue(self, "area")
        event.init_events_area(self)
        self.commands = {'name': ('string', None),
                         'author': ('string', None),
                         'plane': ('string', planes),
                         'hometown': ('string', None),
                         'difficulty': ('string', difficulty),
                         'alignment': ('string', None),
                         'locationx': ('integer', None),
                         'locationy': ('integer', None),
                         'vnumlow': ('integer', None),
                         'vnumhigh': ('integer', None)}
        if os.path.exists(self.area_path):
            self.load()

    def toJSON(self):
        if self.json_version == 1:
            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "name" : self.name,
                        "author" : self.author,
                        "plane" : self.plane,
                        "hometown" : self.hometown,
                        "difficulty" : self.difficulty,
                        "alignment" : self.alignment,
                        "locationx" : self.locationx,
                        "locationy" : self.locationy,
                        "vnumlow" : self.vnumlow,
                        "vnumhigh" : self.vnumhigh}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        # Write new JSON formated Exits for the area.
        for eacharea in arealist:
            for eachroom in eacharea.roomlist:
                theroom = roomByVnum(eachroom)
                for eachexit in theroom.exits:
                    theexit = eacharea.roomlist[eachroom].exits[eachexit]
                    filename = os.path.join(eacharea.folder_path, f"exits/{eachroom}-{eachexit}.json")
                    with open(filename, 'w') as thefile:
                        thefile.write(theexit.toJSON())

        # Write new JSON formatted Rooms for the area.
        for eacharea in arealist:
            for eachroom in eacharea.roomlist:
                theroom = roomByVnum(eachroom)
                filename = os.path.join(eacharea.folder_path, f"rooms/{eachroom}.json")
                with open(filename, 'w') as thefile:
                    thefile.write(theroom.toJSON())

        # Write new JSON formatted Area header for the area.
        for eacharea in arealist:
            filename = os.path.join(eacharea.folder_path, f"{eacharea.name}.json")
            with open(filename, 'w') as thefile:
                thefile.write(eacharea.toJSON())

    def load(self):
        with open(self.area_path, 'r') as thefile:
            data = thefile.read()
        
        # Load Header Data into this Area
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        # Load each Room into this Area
        roomfilepath = os.path.join(self.folder_path, f"rooms/*.json")
        filenames = glob.glob(roomfilepath)
        for eachfile in filenames:
            with open(eachfile, 'r') as thefile:
               room.oneRoom(self, thefile.read())
 

        # Load each Exit and attach it to a room
        exitfilepath = os.path.join(self.folder_path, f"exits/*.json")
        filenames = glob.glob(exitfilepath)
        for eachfile in filenames:
            with open(eachfile, 'r') as thefile:
                fullpath, direction_fn = eachfile.split('.')[0].split('-')
                roomvnum = fullpath.split('/')[-1:][0]
                attached_room = roomByVnum(int(roomvnum))
                if attached_room == False:
                    comm.log(world.serverlog, f"roomByVnum failed in exit load in area.py: {roomvnum}")
                else:
                    exits.Exit(attached_room, direction_fn, thefile.read())

        # Add this area to the area list.
        arealist.append(self)
   
    def display(self):
        return(f"{{WName{{x: {self.name}\n"
               f"{{WAuthor{{x: {self.author}\n"
               f"{{WPlane{{x: {self.plane}\n"
               f"{{WHometown{{x: {self.hometown}\n"
               f"{{WDifficulty{{x: {self.difficulty}\n"
               f"{{WAlignment{{x: {self.alignment}\n"
               f"{{WLocation X{{x: {self.locationx}\n"
               f"{{WLocation Y{{x: {self.locationy}\n"
               f"{{WVnum Low{{x: {self.vnumlow}\n"
               f"{{WVnum High{{x: {self.vnumhigh}\n")

