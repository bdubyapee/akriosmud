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

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp open{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}

@Command(**requirements)
def open(caller, args):
    if args in caller.location.exits.keys():
        exit = caller.location.exits[args]
        if exit.destination in area.roomlist.keys():
            # Does the exit have a door and is it closed?
            if exit.hasdoor == 'true':
                if exit.dooropen == 'true':
                    caller.write("The door in that direction is already open.")
                    return
                if exit.locked == 'true' or exit.magiclocked == 'true':
                    caller.write("It won't open!")
                    return
                exit.dooropen = 'true'
                caller.write(f"You open the {exit.keywords[0]}.")
                return
            else:
                caller.write("There is no door in that direction")
                return
        else:
            # ReWrite here for exiting areas into the map and/or other areas.
            caller.write("That exit appears to be broken!")
    else:
        caller.write("There is no door in that direction")

