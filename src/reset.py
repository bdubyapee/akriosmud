#! usr/bin/env python
# Project: Akrios
# Filename: reset.py
# 
# File Description: Module dealing with resets for mobiles, objects, shops, etc.
# 
# By: Jubelo

from collections import namedtuple
import json

import olc
import event


# Define some named tuples for varios reset values.

ResetType = namedtuple("ResetType", "name")

reset_type = {"mobile": ResetType("mobile"),
              "object": ResetType("object")}

class Reset(olc.Editable):
    CLASS_NAME = "__Reset__"
    FILE_VERSION = 1

    def __init__(self, area, data=None):
        super().__init__()
        self.json_version = Reset.FILE_VERSION
        self.json_class_name = Reset.CLASS_NAME
        self.area = area
        self.aid = str(uuid.uuid4())
        self.target_vnum = 0
        self.target_max_amount = 0
        self.target_type = None
        self.target_load_loc = 0
        self.target_mobile_wear = False
        self.events = event.Queue(self, "reset")
        event.init_events_reset(self)
        self.commands = {"target_vnum": ("integer", None),
                         "target_max_amount": ("integer", None),
                         "target_load_loc": ("integer", None),
                         "target_type": ("string", reset_type),
                         "target_mobile_wear": ("string", ['true', 'false'])}
        if data is not None:
            self.load(data)

    def toJSON(self):
        if self.json_version == 1:
            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "aid" : self.aid,
                        "target_vnum" : self.target_vnum,
                        "target_max_amount" : self.target_max_amount,
                        "target_type" : self.target_type,
                        "target_load_loc" : self.target_load_loc,
                        "target_mobile_wear": self.target_mobile_wear}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        self.area.resetlist[self.vnum] = self

    def display(self):
        return(f"{{BArea{{x: {self.area.name}\n"
               f"{{BAid{{x: {self.aid}\n"
               f"{{BTarget_vnum{{x: {self.target_vnum}\n"
               f"{{BTarget_max_amount{{x: {self.target_max_amount}\n"
               f"{{BTarget_type{{x: {self.target_type}\n"
               f"{{BTarget_load_loc{{x: {self.target_load_loc}\n"
               f"{{BTarget_mobile_wear{{x: {self.target_mobile_wear}\n")


