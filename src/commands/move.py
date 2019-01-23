# Project: Akrios
# Filename: commands/move.py
#
# Capability: player
# 
# Command Description: Underlying command for a player to move in a direction
#
#
# By: Jubelo

from commands import *

name = "move"
version = 1


requirements = {'capability': 'player',
                'generic_fail': "See {WHelp move{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sitting', 'is_sleeping']}

@Command(**requirements)
def move(caller, args):
    if args in caller.location.exits:
        exit = caller.location.exits[args]
        if exit.destination in area.roomlist:
            # Does the exit have a door and is it closed?
            if exit.hasdoor == 'true' and exit.dooropen == 'false':
                caller.write("The door in that direction is closed.")
                return
            # Are we too tall to fit in that exit?
            heightnow = caller.height['feet'] * 12 + caller.height['inches']
            if exits.exit_sizes[exit.size].height < heightnow:
                caller.write("You will not fit!")
                return

            # We have passed all validity checks to move.  Housekeeping and move the thing.
            if caller.is_building:
                Command.commandhash['roomedit'](caller, 'done')
                wasBuilding = True
            else:
                wasBuilding = False
            newroom = area.roomByVnum(exit.destination)
            caller.move(newroom, caller.location, args)
            caller.interp("look")
            if wasBuilding:
                Command.commandhash['roomedit'](caller, str(exit.destination))            
        else:
            caller.write("That exit appears to be broken!")
    else:
        caller.write("You can't go in that direction.")

