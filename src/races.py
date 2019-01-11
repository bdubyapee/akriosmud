#! usr/bin/env python
# Project: Akrios
# Filename: races.py
# 
# File Description: Module to deal with races.
# 
# By: Jubelo

import os
import glob
import json

import olc
import world



WRITE_NEW_FILE_VERSION = False

sizelist = ('tiny', 'small', 'medium', 'large', 'huge')
alignment = ('lawful good', 'lawful neutral', 'lawful evil',
             'neutral good', 'neutral', 'neutral evil',
             'chaotic good', 'chaotic neutral', 'chaotic evil')
bodypartslist = ('head', 'face', 'hand', 'leg', 'foot', 'nose', 'ear', 'scalp', 'torso', 'finger',
                 'toe', 'entrails', 'wing', 'tail', 'snout', 'shell', 'antenna', 'paw',
                 'fin', 'scale', 'rattle', 'tongue', 'eye', 'skull', 'arm', 'bone', 'pelt', 'heart',
                 'liver', 'stomach', 'kidney', 'lung', 'gills', 'claw', 'beak', 'feather',
                 'whisker', 'tooth', 'tusk', 'horn', 'hoof', 'hide', 'tentacle', 'mane', 'mandible',
                 'thorax')
wearlocationslist = ('head', 'face', 'eyes', 'neck', 'left arm', 'right arm',
                     'right forearm', 'left forearm', 'finger', 'left hand',
                     'right hand', 'torso', 'back', 'waist', 'left leg',
                     'right leg', 'left shin', 'right shin', 'left foot',
                     'right foot', 'left shoulder', 'right shoulder',
                     'upper right arm', 'upper left arm', 
                     'upper right hand', 'upper left hand', 'upper right forearm',
                     'upper left forearm', 'horns', 'floating nearby', 'tail')

height_list_values = [number for number in range(12)]
ac_and_resistance_values = [number for number in range(-50, 51)]
start_locationlist = {'drowhome': 101,  'stormhaven': 101, 'whitestone keep':101}
special_skillslist = ['drow', 'elven', 'high elven', 'common']



class oneRace(olc.Editable):
    CLASS_NAME = "__oneRace__"
    FILE_VERSION = 1


    def __init__(self, path):
        super().__init__()
        
        self.path = path
        self.json_version = oneRace.FILE_VERSION
        self.json_class_name = oneRace.CLASS_NAME
        self.builder = None
        self.name = ''
        self.description = ''
        self.alignment = []
        self.playable = 'false'
        self.descriptive = ''
        self.size = ''
        self.heightfeet = 0
        self.heightinches = 0
        self.undead = 'false'
        self.weight = 0
        self.ageminimum = 0
        self.agemaximum = 0
        self.ba_slashing = 0
        self.ba_bashing = 0
        self.ba_piercing = 0
        self.ba_lashing = 0
        self.br_fire = 0
        self.br_ice = 0
        self.br_lightning = 0
        self.br_earth = 0
        self.br_disease = 0
        self.br_poison = 0
        self.br_magic = 0
        self.br_holy = 0
        self.br_mental = 0
        self.br_physical = 0
        self.wearlocations = []
        self.bodyparts = []
        self.skin = []
        self.eyes = []
        self.hair = []
        self.speed = 0
        self.agility = 0
        self.strength = 0
        self.intelligence = 0
        self.wisdom = 0
        self.charisma = 0
        self.luck = 0
        self.constitution = 0
        self.start_location = {}
        self.special_skills = {}
        self.commands = {'name': ('string', None),
                         'description': ('description', None),
                         'alignment': ('list', alignment),
                         'playable': ('string', ['true', 'false']),
                         'descriptive': ('string', None),
                         'size': ('string', sizelist),
                         'heightfeet': ('integer', height_list_values),
                         'heightinches': ('integer', height_list_values),
                         'undead': ('string', ['true', 'false']),
                         'weight': ('integer', None),
                         'ageminimum': ('integer', None),
                         'agemaximum': ('integer', None),
                         'ba_slashing': ('integer', ac_and_resistance_values),
                         'ba_bashing': ('integer', ac_and_resistance_values),
                         'ba_piercing': ('integer', ac_and_resistance_values),
                         'ba_lashing': ('integer', ac_and_resistance_values),
                         'br_fire': ('integer', ac_and_resistance_values),
                         'br_ice': ('integer', ac_and_resistance_values),
                         'br_lightning': ('integer', ac_and_resistance_values),
                         'br_earth': ('integer', ac_and_resistance_values),
                         'br_disease': ('integer', ac_and_resistance_values),
                         'br_poison': ('integer', ac_and_resistance_values),
                         'br_magic': ('integer', ac_and_resistance_values),
                         'br_holy': ('integer', ac_and_resistance_values),
                         'br_mental': ('integer', ac_and_resistance_values),
                         'br_physical': ('integer', ac_and_resistance_values),
                         'wearlocations': ('list', wearlocationslist),
                         'bodyparts': ('list', bodypartslist),
                         'skin': ('list', None),
                         'eyes': ('list', None),
                         'hair': ('list', None),
                         'speed': ('integer', None),
                         'agility': ('integer', None),
                         'strength': ('integer', None),
                         'intelligence': ('integer', None),
                         'wisdom': ('integer', None),
                         'charisma': ('integer', None),
                         'luck': ('integer', None),
                         'constitution': ('integer', None),
                         'start_location': ('dict', (list(start_locationlist.keys()),
                                                     list(start_locationlist.values()))),
                         'special_skills': ('list', special_skillslist)}
        if os.path.exists(path):
            self.load()

    def load(self):
        with open(self.path, "r") as thefile:
            race_file_dict = json.loads(thefile.read())
            for eachkey, eachvalue in race_file_dict.items():
                setattr(self, eachkey, eachvalue)

    def toJSON(self):
        if self.json_version == 1:
            jsonable = {'json_version' : self.json_version,
                        'json_class_name' : self.json_class_name,
                        'name' : self.name,
                        'description' : self.description,
                        'alignment' : self.alignment,
                        'playable' : self.playable,
                        'descriptive' : self.descriptive,
                        'size' : self.size,
                        'heightfeet' : self.heightfeet,
                        'heightinches' : self.heightinches,
                        'undead' : self.undead,
                        'weight' : self.weight,
                        'ageminimum' : self.ageminimum,
                        'agemaximum' : self.agemaximum,
                        'ba_slashing' : self.ba_slashing,
                        'ba_bashing' : self.ba_bashing,
                        'ba_piercing' : self.ba_piercing,
                        'ba_lashing' : self.ba_lashing,
                        'br_fire' : self.br_fire,
                        'br_ice' : self.br_ice,
                        'br_lightning' : self.br_lightning,
                        'br_earth' : self.br_earth,
                        'br_disease' : self.br_disease,
                        'br_poison' : self.br_poison,
                        'br_magic' : self.br_magic,
                        'br_holy' : self.br_holy,
                        'br_mental' : self.br_mental,
                        'br_physical' : self.br_physical,
                        'wearlocations' : self.wearlocations,
                        'bodyparts' : self.bodyparts,
                        'skin' : self.skin,
                        'eyes' : self.eyes,
                        'hair' : self.hair,
                        'speed' : self.speed,
                        'agility' : self.agility,
                        'strength' : self.strength,
                        'intelligence' : self.intelligence,
                        'wisdom' : self.wisdom,
                        'charisma' : self.charisma,
                        'luck' : self.luck,
                        'constitution' : self.constitution,
                        'start_location' : self.start_location,
                        'special_skills' : self.special_skills}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        if self.json_version == 1:
            with open(f"{self.path}.json", "w") as thefile:
                thefile.write(self.toJSON())
                

    def display(self):
        retvalue = "Name: {0}\n\r"\
                   "Alignment: {1}\n\r"\
                   "Playable: {2}\n\r"\
                   "Descriptive: {3}\n\r"\
                   "Size: {4}\n\r"\
                   "HeightFeet: {5}\n\r"\
                   "HeightInches: {6}\n\r"\
                   "Undead: {7}\n\r"\
                   "Weight: {8}\n\r"\
                   "AgeMinimum: {9}\n\r"\
                   "AgeMaximum: {10}\n\r"\
                   "BaSlashing: {11}\n\r"\
                   "BaBashing: {12}\n\r"\
                   "BaPiercing: {13}\n\r"\
                   "BaLashing: {14}\n\r"\
                   "BrFire: {15}\n\r"\
                   "BrIce: {16}\n\r"\
                   "BrLightning: {17}\n\r"\
                   "BrEarth: {18}\n\r"\
                   "BrDisease: {19}\n\r"\
                   "BrPoison: {20}\n\r"\
                   "BrMagic: {21}\n\r"\
                   "BrHoly: {22}\n\r"\
                   "BrMental: {23}\n\r"\
                   "BrPhysical: {24}\n\r"\
                   "Skin: {25}\n\r"\
                   "Eyes: {26}\n\r"\
                   "Hair: {27}\n\r"\
                   "Speed: {28}\n\r"\
                   "Agility: {29}\n\r"\
                   "Strength: {30}\n\r"\
                   "Intelligence: {31}\n\r"\
                   "Wisdom: {32}\n\r"\
                   "Charisma: {33}\n\r"\
                   "Luck: {34}\n\r"\
                   "Constitution: {35}\n\r"\
                   "WearLocations: {36}\n\r"\
                   "BodyParts: {37}\n\r"\
                   "Start Locations: {38}\n\r"\
                   "Special Skills: {39}\n\r"\
                   "Description:\n\r"\
                   "{40}...\n\r".format(
                      self.name.capitalize(), self.alignment,
                      self.playable, self.descriptive,
                      self.size, self.heightfeet, self.heightinches,
                      self.undead,
                      self.weight, self.ageminimum, self.agemaximum,
                      self.ba_slashing, self.ba_bashing, self.ba_piercing, self.ba_lashing,
                      self.br_fire, self.br_ice, self.br_lightning,
                      self.br_earth, self.br_disease, self.br_poison,
                      self.br_magic, self.br_holy, self.br_mental,
                      self.br_physical,
                      self.skin, self.eyes, self.hair, self.speed,
                      self.agility, self.strength,
                      self.intelligence, self.wisdom, self.charisma,
                      self.luck, self.constitution,
                      self.wearlocations, self.bodyparts,
                      self.start_location,
                      self.special_skills,
                      self.description[:180])
        return retvalue
   
goodraces = []
neutralraces = []
evilraces = []
racesdict = {}

def init():
    racepaths = glob.glob(os.path.join(world.raceDir, '*.json'))
    for racepath in racepaths:
        therace = oneRace(racepath)
        addtolist(therace)
        if WRITE_NEW_FILE_VERSION:
            therace.save()

def reload():
    racesdict = {}
    goodraces = []
    neutralraces = []
    evilraces = []
    init()

def addtolist(race):
    racesdict[race.name.lower()] = race
    alignments = {'lawful good' : goodraces,
                  'neutral good' : goodraces,
                  'chaotic good' : goodraces,
                  'lawful neutral' : neutralraces,
                  'neutral' : neutralraces,
                  'chaotic neutral' : neutralraces,
                  'lawful evil' : evilraces,
                  'neutral evil' : evilraces,
                  'chaotic evil' : evilraces}
    if race.alignment[0].lower() in alignments and race.playable == 'true':
        alignments[race.alignment[0]].append(race.name.lower())

def racebyname(name):
    if name in racesdict:
        return racesdict[name]
    else:
        raise SyntaxError('Thats not a race I recognize.')

def race_names_by_alignment(alignment = "good"):
    if alignment == "good":
        return ', '.join(goodraces)
    elif alignment == "neutral":
        return ', '.join(neutralraces)
    elif alignment == "evil":
        return ', '.join(evilraces)
    else:
        raise SyntaxError("races.py That is not an alignment I recognize.")

