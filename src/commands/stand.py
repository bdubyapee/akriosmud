#! /usr/bin/env python3
# Project: Akrios
# filename: commands/stand.py
#
# Capability: player
#
# Command Description: Allows the player to stand up.
#
#
# By: Jubelo

from commands import *

name = "stand"
version = 1

@Command(capability='player')
def stand(caller, args):
    if hasattr(caller, "position"):
        if caller.position == "standing":
            caller.write("You are already standing")
            return
        elif caller.position == "sitting":
            caller.position = "standing"
            caller.write("You stand up.")
            return
        elif caller.position == "sleeping":
            caller.position = "standing"
            caller.write("You awaken and stand up.")
            return

