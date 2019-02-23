#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/inventoy.py
#
# Capability: player, mobile
#
# Command Description: A command which players can use to check their inventory.
#
#
# By: Jubelo

from commands import *

name = "inventory"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp inventory{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def inventory(caller, args, **kwarg):

    caller.write("Items currently in your inventory:")
    caller.write("")

    if not caller.contents:
        caller.write("You are carrying nothing.")
        return

    work_around = 0

    for aid, object_ in caller.contents.items():
        if aid in caller.equipped.values():
            work_around += 1
            continue
        caller.write(f"{object_.vnum:6} {object_.disp_name:25} {aid}")

    if work_around > 0:
        caller.write("You are carrying nothing.")
