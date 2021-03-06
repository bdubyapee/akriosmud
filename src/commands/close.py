# Project: Akrios
# Filename: commands/close.py
#
# Capability: player
# 
# Command Description: Allows a player to close a thing.  Exits only for now.
#
#
# By: Jubelo

from commands import *

name = "close"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp close{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
def close(caller, args, **kwargs):
    if args in caller.location.exits:
        exit_ = caller.location.exits[args]
        if exit_.destination in caller.location.area.roomlist:
            # Does the exit have a door and is it closed?
            if exit_.hasdoor == 'true':
                if exit_.locked == 'true' or exit_.magiclocked == 'true':
                    caller.write("It won't open!")
                    return
                if exit_.dooropen == 'true':
                    exit_.dooropen = 'false'
                    caller.write(f"You close the {exit_.keywords[0]}.")
                    return
                if exit_.dooropen == 'false':
                    caller.write("But it' already closed!")
                    return
            else:
                caller.write("There is no door in that direction")
                return
        else:
            # ReWrite this because we'll have exits to other areas and/or the map.
            caller.write("That exit appears to be broken!")
    else:
        caller.write("There is no door in that direction")
