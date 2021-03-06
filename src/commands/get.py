#! usr/bin/env python3
# Project: Akrios
# filename: commands/get.py
#
# Capability : player, mobile
#
# Command Description: The get command for players.
#
# By: Jubelo

from commands import *

name = "get"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp get{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping'],
                'target': 'target_single_thing_room_nopost'}


@Command(**requirements)
def get(caller, args, **kwargs):

    target = kwargs['target']
    
    # Check weight of thing picked up or cancel

    if target.is_mobile or target.is_player:
        caller.write("You cannot pick up players or mobiles, yet.")
        return

    caller.contents[target.aid] = target
    target.location.contents.remove(target)
    target.location = None
    if target in caller.location.area.objectlist:
        caller.location.area.objectlist.remove(target)

    caller.write(f"You pick up a {target.disp_name}") 
    comm.message_to_room(caller.location, caller, f"{caller.disp_name} picks up a {target.disp_name}")
