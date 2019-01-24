#! usr/bin/env python
# Project: Akrios
# Filename: helpsys.py
# 
# File Description: Module to handle the help system.
# 
# By: Jubelo

from collections import namedtuple
import os
import glob
import time
import json

import comm
import olc
import world



WRITE_NEW_FILE_VERSION = False


# Define some named tuples for various Help file values
Section = namedtuple("Section", "name")

sections = {"player": Section("player"),
            "administrative": Section("administrative"),
            "builder": Section("builder"),
            "deity": Section("deity")}


class oneHelp(olc.Editable):
    CLASS_NAME = "__oneHelp__"
    FILE_VERSION = 1

    def __init__(self, path):
        super().__init__()

        self.path = path
        self.json_version = oneHelp.FILE_VERSION
        self.json_class_name = oneHelp.CLASS_NAME
        self.builder = None
        self.creator = ""
        self.viewable = ""
        self.keywords = []
        self.topics = ""
        self.section = ""
        self.description = ""
        self.commands = {"viewable": ("string", ["true", "false"]),
                         "creator": ("string", None),
                         "keywords": ("list", None),
                         "topics": ("string", None),
                         "section": ("string", sections),
                         "description": ("description", None)}

        if os.path.exists(path):
            self.load()

    def toJSON(self):
        if self.json_version == 1:
            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "creator" : self.creator,
                        "viewable" : self.viewable,
                        "keywords" : self.keywords,
                        "topics" : self.topics,
                        "section" : self.section,
                        "description" : self.description}
        return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self):
        if self.path.endswith("json"):
            with open(self.path, "r") as thefile:
                help_file_dict = json.loads(thefile.read())
                for eachkey, eachvalue in help_file_dict.items():
                    setattr(self, eachkey, eachvalue)

    def save(self):
        with open(f"{self.path}", "w") as thefile:
            thefile.write(self.toJSON())

    def display(self):
        return (f"{{WCreator{{x: {self.creator}\n"
                f"{{WViewable{{x: {self.viewable}\n"
                f"{{WKeywords{{x: {self.keywords}\n"
                f"{{WTopics{{x: {self.topics}\n"
                f"{{WSection{{x: {self.section}\n"
                f"{{WDescription{{x:\n\r"
                f"{self.description[:190]}|...\n\r")


helpfiles = {}


def init():
    allhelps = glob.glob(os.path.join(world.helpDir, "*.json"))
    for singlehelp in allhelps:
        thehelp = oneHelp(singlehelp)
        for keyword in thehelp.keywords:
            helpfiles[keyword] = thehelp
        if WRITE_NEW_FILE_VERSION:
            thehelp.save()


def reload():
    helpfiles = {}
    init()


def get_help(key, server=False):
    key = key.lower()
    if key != '':
        if key in helpfiles:
            if helpfiles[key].viewable.lower() == "true" or server == True:
                return helpfiles[key].description
        else:
            filename = os.path.join(world.logDir, "missinghelp")
            with open(filename, "a+") as thefile:
                thefile.write(f"{time.asctime()}> {key}\n")
            return "We do not appear to have a help file for that topic. "\
                   "We have however logged the attempt and will look into creating "\
                   "a help file for that topic as soon as possible.\n\r"


