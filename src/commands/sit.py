#! /usr/bin/env python3
# Project: Akrios
# filename: commands/sit.py
#
# Capability: player
#
# Command Description: Allows the player to sit down.
#
#
# By: Jubelo

from commands import *

name = "sit"
version = 1

@Command(capability='player')
def sit(caller, args):
    if hasattr(caller, "position"):
        if caller.position == "sitting":
            caller.write("You are already sitting")
            return
        elif caller.position == "standing":
            caller.position = "sitting"
            caller.write("You sit down.")
            message = f"{caller.name.capitalize()} sits down."
            comm.message_to_room(caller.location, caller, message)
            return
        elif caller.position == "sleeping":
            caller.position = "sitting"
            caller.write("You wake up and begin sitting")
            message = f"{caller.name.capitalize()} sits up and looks around."
            comm.message_to_room(caller.location, caller, message))
            caller.interp("look")
            return

