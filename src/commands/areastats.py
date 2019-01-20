# Project: Akrios
# Filename: commands/areastats.py
#
# Capability: builder
#
# Command Description: Provides details about the area currently in.
#
# By: Jubelo

from commands import *

name = "areastats"
version = 1

requirements = {'capability': 'builder',
                'generic_fail': "See {WHelp areastats{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def areastats(caller, args):
    caller.write(caller.location.area.display())
    caller.write("")
    arearoomlist = caller.location.area.roomlist
    caller.write("{RRooms in this area{x:")
    for oneroom in arearoomlist.keys():
        currentroom = arearoomlist[oneroom]
        caller.write(f"{{W[{{B{currentroom.vnum}{{W]{{x {currentroom.name.capitalize()}")


