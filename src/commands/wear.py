#! usr/bin/env python3
# Project: Akrios
# filename: commands/wear.py
#
# Capability : player, mobile
#
# Command Description: The wear command for players.
#
# By: Jubelo

from commands import *

name = "wear"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp wear{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}

@Command(**requirements)
def wear(caller, args, **kwargs):
    '''
        Expecting:
                    "helmet on head"
                    "bracelet on left wrist"
    '''

    target = None
    location = None
    args = args.lower()

    if not args:
        caller.write("What would you like to wear?")
        return

    if ' on ' in args:
        target_text, location = args.split(' on ')
        target_text = target_text.strip()
        location = location.strip()
    else:
        caller.write("Please specify where to wear it.")
        caller.write("Example: wear helmet on head.")
        return

    for aid, object_ in caller.contents.items():
        if object_.disp_name.startswith(target_text) and aid not in caller.equipped.values():
            target = object_
            break
        for eachkw in object_.keywords:
            thekey = eachkw.lower()
            if thekey.startswith(target_text) and aid not in caller.equipped.values():
                target = object_
                break

    if target is None:
        caller.write(f"You don't seem to have a {args}.")
        return

    if location not in caller.equipped:
        caller.write(f"You cannot wear something on a wear location you don't have.")
        return

    if location is not None and caller.equipped[location] is not None:
        caller.write(f"You are already wearing something in that location.")
        return

    if location not in object_.allowable_wear_loc:
        caller.write(f"You cannot wear a {args} there!")
        return

    caller.equipped[location] = target.aid    
    caller.write(f"You wear a {target.disp_name} on your {location}.")
    comm.message_to_room(caller.location, caller, f"{caller.disp_name} wears a {target.disp_name}.")

