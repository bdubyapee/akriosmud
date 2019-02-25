#! usr/bin/env python
# Project: Akrios
# Filename: reset.py
# 
# File Description: Module dealing with resets for mobiles, objects, shops, etc.
# 
# By: Jubelo

from collections import namedtuple
import json
import uuid

import mobile
import objects
import olc
import event


# Define some named tuples for varios reset values.

ResetType = namedtuple("ResetType", "name")

reset_type = {"mobile": ResetType("mobile"),
              "object": ResetType("object"),
              "shop": ResetType("shop")}


class BaseReset(object):
    def __init__(self):
        super().__init__()
        self.aid = str(uuid.uuid4())
        self.target_vnum = 0
        self.target_max_amount = 0
        self.target_type = None
        self.target_loc_vnum = 0

    def basetoJSON(self):
        jsonable = {"target_vnum": self.target_vnum,
                    "target_max_amount": self.target_max_amount,
                    "target_type": self.target_type,
                    "target_loc_vnum": self.target_loc_vnum}
        return jsonable


class MobileReset(BaseReset):
    def __init__(self, area=None, data=None):
        super().__init__()
        self.area = area

        if data is not None:
            self.load(data)

    def toJSON(self):
        jsonable = self.basetoJSON()

        return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        if type(self.target_loc_vnum) is str:
            self.target_loc_vnum = int(self.target_loc_vnum)

    def execute(self):
        if self.target_vnum not in mobile.mobilelist_by_vnum_index:
            print(f"Unable to find mobile vnum {self.target_vnum}")
            return

        if self.target_loc_vnum not in self.area.roomlist:
            print(f"Mobile Unable to find room vnum {self.target_loc_vnum}")
            print(f"target_loc_vnum type = {type(self.target_loc_vnum)}")
            print(f"roomlist = {self.area.roomlist}")
            return

        # Count current mobiles of this vnum, if at or exceeding max then bail out. 

        loc = self.target_loc_vnum
        mobile.mobilelist_by_vnum_index[self.target_vnum].create_instance(location=loc)


class ObjectReset(BaseReset):
    def __init__(self, area=None, data=None):
        super().__init__()
        self.area = area
        self.target_loc_is = ''
        self.target_mobile_wear = False

        if data is not None:
            self.load(data)

    def toJSON(self):
        jsonable = self.basetoJSON()
        jsonable["target_loc_is"] = self.target_loc_is
        jsonable["target_mobile_wear"] = self.target_mobile_wear

        return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        if type(self.target_loc_vnum) is str:
            self.target_loc_vnum = int(self.target_oc_vnum)

    def execute(self):
        if self.target_vnum not in objects.objectlist_by_vnum_index:
            print(f"Unable to find object vnum {self.target_vnum}")
            return

        if self.target_loc_is == 'room' and self.target_loc_vnum not in self.area.roomlist:
            print(f"Object Unable to find room vnum {self.target_loc_vnum}")
            print(f"target_loc_vnum type = {type(self.target_loc_vnum)}")
            print(f"roomlist = {self.area.roomlist}")
            return

        mli = mobile.mobilelist_by_vnum_index

        if self.target_loc_is == 'mobile' and self.target_loc_vnum not in mli:
            print(f"Unable to find mobile vnum {self.target_loc_vnum}")
            return

        # Count current objects of this vnum, if at or exceeding max then bail out. 

        loc = self.target_loc_vnum

        objects.objectlist_by_vnum_index[self.target_vnum].create_instance(location=loc)


class Reset(olc.Editable):
    CLASS_NAME = "__Reset__"
    FILE_VERSION = 1

    def __init__(self, area=None, data=None):
        super().__init__()
        self.json_version = Reset.FILE_VERSION
        self.json_class_name = Reset.CLASS_NAME
        self.area = area
        self.aid = str(uuid.uuid4())
        self.mobile_list = {}
        self.object_list = {}
        self.shop_list = {}
        self.events = event.Queue(self, "reset")
        event.init_events_reset(self)
        self.commands = {"target_type": ("string", reset_type),
                         "mobile": ("string", None),
                         "object": ("string", None),
                         "shop": ("string", None)}
        if data is not None:
            self.load(data)

    def toJSON(self):
        if self.json_version == 1:

            mob_list = {int(k): v.toJSON() for k,v in self.mobile_list.items()}
            obj_list = {int(k): v.toJSON() for k,v in self.object_list.items()}
            shp_list = {int(k): v.toJSON() for k,v in self.shop_list.items()}

            jsonable = {"json_version" : self.json_version,
                        "json_class_name" : self.json_class_name,
                        "aid" : self.aid,
                        "mobile_list" : mob_list or {},
                        "object_list" : obj_list or {},
                        "shop_list" : shp_list or {}}

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        self.mobile_list = {int(k): MobileReset(self.area, v) for k,v in self.mobile_list.items()}
        self.object_list = {int(k): ObjectReset(self.area, v) for k,v in self.object_list.items()}
        self.shop_list = {int(k): ShopReset(self.area, v) for k,v in self.shop_list.items()}

        if self.mobile_list:
            for each_reset in self.mobile_list.values():
                each_reset.execute()
        if self.object_list:
            for each_reset in self.object_list.values():
                each_reset.execute()

        self.area.resetlist = self

    def display(self):
        return(f"{{BArea{{x: {self.area.name}\n"
               f"{{BAid{{x: {self.aid}\n")
