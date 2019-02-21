#! usr/bin/env python3
# Project: Akrios
# filename: commands/drop.py
#
# Capability : player, mobile
#
# Command Description: The drop command for players.
#
# By: Jubelo

from commands import *

name = "drop"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp drop{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}

@Command(**requirements)
def drop(caller, args, **kwargs):

    target = None
    args = args.lower()

    for aid, object_ in caller.contents.items():
        if object_.disp_name.startswith(args):
            target = object_
            continue
        for eachkw in object_.keywords:
            thekey = eachkw.lower()
            if thekey.startswith(args):
                target = object_
                continue

    if target is None:
        caller.write(f"You don't seem to have a {args}.")
        return

    caller.location.area.objectlist.append(target)
    caller.contents.pop(target.aid)

    target.location = caller.location
    target.location.contents.append(target)
    caller.write(f"You drop a {target.disp_name}")
    comm.message_to_room(caller.location, caller, f"{caller.disp_name} drops a {target.disp_name}")

