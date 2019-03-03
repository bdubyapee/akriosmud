#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/equipped.py
#
# Capability: player, mobile
#
# Command Description: A command which players can use to check their equipped items.
#
#
# By: Jubelo

from commands import *

name = "equipped"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp equipped{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def equipped(caller, args, **kwarg):

    caller.write("Items currently equipped:")
    caller.write("")

    for each_loc, each_aid in caller.equipped.items():
        eq_name = ''
        if caller.equipped[each_loc] is None:
            eq_name = "nothing"
        else:
            eq_name = caller.contents[each_aid].disp_name
        caller.write(f"  <{each_loc:17}>   {eq_name:40}")

    caller.write("")
