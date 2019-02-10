#! usr/bin/env python
# Project: Akrios
# Filename: livingthing.py
# 
# File Description: The livingthing module.  All living things inherit from this.
#                   This includes mobiles and players.
# 
# By: Jubelo

# Imports here
from collections import namedtuple
import time

import area
import comm
import commands
import exits
import helpsys
import races
import room


# Define named tuples for living things.

Position = namedtuple("Position", "name")

positions = {"crawling": Position("crawling"),
             "sleeping": Position("sleeping"),
             "laying": Position("laying"),
             "sitting": Position("sitting"),
             "standing": Position("standing")}


Gender = namedtuple("Gender", "name")

genders = {"male": Gender("male"),
           "female": Gender("female"),
           "other": Gender("other")}


Discipline = namedtuple("Discipline", "name")

disciplines = {"physical": Discipline("physical"),
               "mental": Discipline("mental"),
               "mystic": Discipline("mystic"),
               "religious": Discipline("religious")}


StatType = namedtuple("StatType", "name")

stat_type_strength = StatType("strength")
stat_type_agility = StatType("agility")
stat_type_speed = StatType("speed")
stat_type_intelligence = StatType("intelligence")
stat_type_wisdom = StatType("wisdom")
stat_type_charisma = StatType("charisma")
stat_type_luck = StatType("luck")
stat_type_constitution = StatType("constitution")

stat_types = {"strength": stat_type_strength,
              "agility": stat_type_agility,
              "speed": stat_type_speed,
              "intelligence": stat_type_intelligence,
              "wisdom": stat_type_wisdom,
              "charisma": stat_type_charisma,
              "luck": stat_type_luck,
              "constitution": stat_type_constitution}


class LivingThing(object):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.lastname = ''
        self.long_description = ''
        self.short_description = ''
        self.gender = 'male'
        self.location = None
        self.contents = []
        self.capability = []
        self.last_input = 0
        self.race = None
        self.aid = 0
        self.age = 1
        self.level = 1
        self.alignment = 'neutral'
        self.exp = {'combat': 0,
                    'explore': 0,
                    'profession': 0}
        self.maximum_stat = {'strength': 1, 'agility': 1, 'speed': 1, 'intelligence': 1,
                             'wisdom': 1, 'charisma': 1, 'luck': 1, 'constitution': 1}
        self.current_stat = {'strength': 1, 'agility': 1, 'speed': 1, 'intelligence': 1,
                             'wisdom': 1, 'charisma': 1, 'luck': 1, 'constitution': 1}
        self.money = {'copper': 0,
                      'silver': 0,
                      'gold': 0,
                      'platinum': 0}
        self.height = {'feet': 5,
                       'inches': 1}
        self.weight = 1
        self.hunger = 0
        self.thirst = 0
        self.wimpy = 0
        self.maxhp = 1
        self.currenthp = 1
        self.maxmovement = 1
        self.currentmovement = 1
        self.maxwillpower = 0
        self.currentwillpower = 0
        self.hitroll = 0
        self.damroll = 0
        self.totalmemoryslots = {'first circle' : 0,
                                 'second circle' : 0,
                                 'third circle': 0,
                                 'fourth circle': 0,
                                 'fifth circle': 0,
                                 'sixth circle': 0,
                                 'seventh circle': 0,
                                 'eighth circle': 0,
                                 'ninth circle': 0}
        self.memorizedspells = {}
        self.guild = None
        self.council = None
        self.family = None
        self.clan = None
        self.deity = ''
        self.discipline = None
        self.inventory = []
        self.worn = {}
        self.baceac = {'slashing' : 0,
                       'piercing' : 0,
                       'bashing' : 0,
                       'lashing' : 0}
        self.currentac = {'slashing' : 0,
                          'piercing' : 0,
                          'bashing' : 0,
                          'lashing' : 0}
        self.position = None
        self.knownpeople = {}
        self.alias = {}
        self.snooped_by = []


    def addKnown(self, idnum=None, name=None):
        if idnum == None or name == None:
            comm.wiznet("You must provide id and name arguments.  addKnown:livingthing.py")
        else:
            self.knownpeople[idnum] = name

    def interp(self, inp=None):

        if len(self.snooped_by) > 0:
            for each_person in self.snooped_by:
                each_person.write(f"{self.name} typed: {inp}")

        inp = inp.split()

        if hasattr(self, 'capability'):
            self.oocflags['afk'] = False

        isBuilding = hasattr(self, 'building')
        isEditing = hasattr(self, 'editing')

        self.last_input = time.time()

        if len(inp) == 0:
            if isBuilding and not isEditing:
                self.write(self.building.display())
                return
            if isEditing:
                self.editing.add('')
                return
            else:
                self.write('')
                return

        # Look in living thing command alias dict, swap alias for full command if found        
        if inp[0] in self.alias:
            inp[0] = self.alias[inp[0]]

        comfind = []

        # Added some time ago for OLC to work properly.  Fix this XXX
        if len(inp) <= 0:
            inp = ['']

        for item in sorted(commands.Command.commandhash.keys()):
            if item.startswith(inp[0].lower()):
                comfind.append(commands.Command.commandhash[item])

        if isBuilding:
            types = {helpsys.oneHelp: 'helpedit',
                     races.oneRace: 'raceedit',
                     area.oneArea: 'areaedit',
                     room.oneRoom: 'roomedit',
                     exits.Exit: 'exitedit'}
            if self.building.__class__ in types:
                comfind.append(commands.Command.commandhash[types[self.building.__class__]])
                # If the person is building we prepend the command they are using.
                inp.insert(0, types[self.building.__class__])
                self.write('')

        if len(comfind) > 0:
            try:
                if isEditing:
                    comfind[-1](self, ' '.join(inp[1:]))
                elif isBuilding:
                    if comfind[0].__name__ not in types.values():
                        comfind[0](self, ' '.join(inp[2:]))
                    else:
                        comfind[0](self, ' '.join(inp[1:]))
                else:
                    comfind[0](self, ' '.join(inp[1:]))
            except (NameError, IndexError) as msg:
                self.write(msg)
        else:
            self.write("Huh?")

    def move(self, tospot=None, fromspot=None, direction=None):
        if tospot == None:
            comm.wiznet("Received None value in move:livingthing.py")
        else:
            mover = self.name.capitalize()
            if direction == None:
                rev_direction = "the ether"
            elif direction != "goto":
                rev_direction = exits.oppositedirection[direction]

            if fromspot != None:
                if direction == "goto":
                    fromspot_message = f"{mover} has vanished into thin air."
                else:
                    fromspot_message = f"{mover} has left to the {direction}."
                comm.message_to_room(fromspot, self, fromspot_message)
                fromspot.contents.remove(self)

            # Once object notification is in, notify left room of departure and
            # room we moved to of arrival.

            tospot.contents.append(self)
            self.location = tospot
            if direction == "goto" or fromspot == None:
                tospot_message = f"{mover} has sprung into existence!"
            else:
                tospot_message = f"{mover} has arrived from the {rev_direction}."
            comm.message_to_room(tospot, self, tospot_message)
            
    def get_known(self, idnum=None):
        if id == None:
            comm.wiznet("You must provide an ID to lookup. get_known:livingthing.py")
            return

        if idnum not in self.knownpeople:
            return ''
        else:
            return self.knownpeople[idnum]

    def write(self, msg):
        if len(self.snooped_by) > 0:
            for each_person in self.snooped_by:
                each_person.write(msg)
         
    @property
    def is_admin(self):
        if 'admin' in self.capability:
            return True
        else:
            return False

    @property
    def is_deity(self):
        if 'deity' in self.capability:
            return True
        else:
            return False

    @property
    def is_builder(self):
        if 'builder' in self.capability:
            return True
        else:
            return False

    @property
    def is_player(self):
        if 'player' in self.capability:
            return True
        else:
            return False

    @property
    def name_cap(self):
        return self.name.capitalize()
