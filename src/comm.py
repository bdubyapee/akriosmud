#! usr/bin/env python
# Project: Akrios
# Filename: comm.py
# 
# File Description: Communications Module.  Handles low level channel/log stuff.
# 
# By: Jubelo

import os
import pytz
import datetime

import player
import world

def wiznet(msg=""):
    msg = f"\n\r\n\r{{YWiznet: {msg.capitalize()[0]}{msg[1:]}{{x"
    log(world.serverlog, msg)
    for person in player.playerlist:
        if person.is_admin:
            person.write(msg)

def act():
    pass

def message_to_player(each_player, sender, message=""):
    if message == "":
        return
    each_player.write(message)
    
def message_to_room(room, sender, message=""):
    if message == "":
        return
    for eachthing in room.contents:
        if eachthing != sender and eachthing.is_player:
            eachthing.write(f"\n\r\n\r{message}")

def message_to_area(area, sender, message=""):
    if message == "":
        return
    for each_player in area.playerlist:
        each_player.write(message)

def log(tofile=None, msg=""):
    if tofile == None:
        wiznet(f"Trying to log to no file in comm.py: {msg}")
    else:
        with open(tofile, "a") as tofile:
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())
            mst_now = utc_now.astimezone(pytz.timezone("America/Denver"))
            tofile.write(f"\n\r{mst_now.isoformat()} : {msg.strip()}")
