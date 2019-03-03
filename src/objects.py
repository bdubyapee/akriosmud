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



PrimaryType = namedtuple("PrimaryType", "name")

primary_types = {"weapon": PrimaryType("weapon"),
                 "armor": PrimaryType("armor"),
                 "food": PrimaryType("food"),
                 "container": PrimaryType("container"),
                 "wand": PrimaryType("wand"),
                 "spell book": PrimaryType("spell book"),
                 "rune": PrimaryType("rune"),
                 "scroll": PrimaryType("scroll"),
                 "key": PrimaryType("key"),
                 "raw material": PrimaryType("raw material"),
                 "craft tool": PrimaryType("craft tool"),
                 "generic": PrimaryType("generic")}



WeaponType = namedtuple("WeaponType", "name dicenum diceside handed")

weapon_types = {"short sword": WeaponType('short sword', 1, 4, 1),
                "dagger": WeaponType('dagger', 1, 2, 1),
                "broad sword": WeaponType('broad sword', 2, 3, 2)}



ArmorType = namedtuple("ArmorType", "name ac_slash ac_bash ac_pierce ac_blud")

armor_types = {"leather helmet": ArmorType('leather helmet', 1, 1, 1, 1),
               "leather shirt": ArmorType('leather shirt', 1, 1, 1, 1),
               "steel helmet": ArmorType('steel helmet', 5, 5, 5, 5)}



FoodType = namedtuple("FoodType", "name")

food_types = {"bread": FoodType("bread")}



DrinkType = namedtuple("DrinkType", "name")

drink_types = {"water": DrinkType("water")}



ContainerType = namedtuple("ContainerType", "name opening liquid maxnum")

container_types = {"bottle": ContainerType('bottle', 'small', True, 30),
                   "vial": ContainerType('vial', 'tiny', True, 1),
                   "flask": ContainerType('flask', 'small', True, 15),
                   "small bag": ContainerType('small bag', 'small', False, 20),
                   "medium bag": ContainerType('medium bag', 'medium', False, 35),
                   "large bag": ContainerType('large bag', 'large', False, 45)}



MaterialType = namedtuple("MaterialType", "name hardness durability")

material_types = {"soft wood": MaterialType('soft wood', 5, 5),
                  "hard wood": MaterialType('hard wood', 10, 10),
                  "stone": MaterialType('stone', 35, 35),
                  "steel": MaterialType('steel', 50, 50),
                  "gold": MaterialType('gold', 25, 25)}


GenericSize = namedtuple("GenericSize", "name")

generic_size_types = {"tiny": GenericSize('tiny'),
                      "small": GenericSize('small'),
                      "medium": GenericSize('medium'),
                      "large": GenericSize('large'),
                      "huge": GenericSize('huge'),
                      "gigantic": GenericSize('gigantic')}


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
        self.weight = 0
        self.generic_size = ''
        self.primary_type = ''
        self.weapon_type = ''
        self.armor_type = ''
        self.food_type = ''
        self.drink_type = ''
        self.container_type = ''
        self.material_type = ''
        self.keywords = []
        self.contents = {}
        self.default_wear_loc = "left hand"
        self.allowable_wear_loc = []

        self.wand_data = {}
        self.spellbook_data = {}
        self.key_data = {}
        self.rune_data = {}
        self.scroll_data = {}
        self.craft_tool_data = {}

        self.area = area
        self.events = event.Queue(self, "object")
        self.commands = {"vnum": ("integer", None),
                         "short_description": ("string", None),
                         "long_description": ("string", None),
                         "name": ("string", None),
                         "weight": ("integer", None),
                         "generic_size": ("string", generic_size_types),
                         "keywords": ("list", None),
                         "default_wear_loc": ("string", races.wearlocationslist),
                         "allowable_wear_loc": ("list", races.wearlocationslist),
                         "primary_type": ("string", primary_types),
                         "weapon_type": ("string", weapon_types),
                         "armor_type": ("string", armor_types),
                         "food_type": ("string", food_types),
                         "drink_type": ("string", drink_types),
                         "container_type": ("string", container_types),
                         "material_type": ("string", material_types),
                         "wand_data": ("dict", (None, None)),
                         "spellbook_data": ("dict", (None, None)),
                         "key_data": ("dict", (None, None)),
                         "rune_data": ("dict", (None, None)),
                         "scroll_data": ("dict", (None, None)),
                         "craft_tool_data": ("dict", (None, None))}

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
                        "weight": self.weight,
                        "generic_size": self.generic_size,
                        "keywords": self.keywords,
                        "contents": self.contents,
                        "default_wear_loc": self.default_wear_loc,
                        "allowable_wear_loc": self.allowable_wear_loc,
                        "primary_type": self.primary_type,
                        "weapon_type": self.weapon_type,
                        "armor_type": self.armor_type,
                        "food_type": self.food_type,
                        "drink_type": self.drink_type,
                        "container_type": self.container_type,
                        "material_type": self.material_type,
                        "vnum": self.vnum,
                        "wand_data": self.wand_data,
                        "spellbook_data": self.spellbook_data,
                        "key_data": self.key_data,
                        "rune_data": self.rune_data,
                        "craft_tool_data": self.craft_tool_data}

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

