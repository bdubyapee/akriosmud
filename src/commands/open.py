# Project: Akrios
# Filename: commands/open.py
#
# Capability: player
# 
# Command Description: Underlying command for a player to open an exit
#
#
# By: Jubelo

from commands import *

name = "open"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp open{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
def open(caller, args, **kwargs):
    if args in caller.location.exits:
        exit_ = caller.location.exits[args]
        if exit_.destination in caller.location.area.roomlist:
            # Does the exit have a door and is it closed?
            if exit_.hasdoor == 'true':
                if exit_.dooropen == 'true':
                    caller.write("The door in that direction is already open.")
                    return
                if exit_.locked == 'true' or exit_.magiclocked == 'true':
                    caller.write("It won't open!")
                    return
                exit_.dooropen = 'true'
                caller.write(f"You open the {exit_.keywords[0]}.")
                return
            else:
                caller.write("There is no door in that direction")
                return
        else:
            # ReWrite here for exiting areas into the map and/or other areas.
            caller.write("That exit appears to be broken!")
    else:
        caller.write("There is no door in that direction")

