#! /usr/bin/env python3
# Project: Akrios
# filename: commands/sleep.py
#
# Capability: player
#
# Command Description: Allows the player to sleep.
#
#
# By: Jubelo

from commands import *

name = "sleep"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp sleep{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def sleep(caller, args, **kwargs):
    if hasattr(caller, "position"):
        if caller.position == "sleeping":
            caller.write("You are already sleeping.")
            return
        elif caller.position == "standing" or caller.position == "sitting":
            caller.position = "sleeping"
            caller.write("You lay down and go to sleep.")
            message = f"{caller.disp_name} lays down to sleep."
            comm.message_to_room(caller.location, caller, message)
            return

