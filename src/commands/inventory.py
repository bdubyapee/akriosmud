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

   if len(caller.contents) == 0:
       caller.write("You are carrying nothing.")
       return

   for aid, object_ in caller.contents.items():
       caller.write(f"{object_.vnum:6} {object_.disp_name:25} {aid}")
