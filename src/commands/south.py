# Project: Akrios
# Filename: commands/south.py
#
# Capability: player
#
# Command Description: Command to move a player south
#
# By: Jubelo

from commands import *

name = "south"
versin = 1

@Command(capability=["player", "mobile"])
def south(caller, args):
    Command.commandhash['move'](caller, 'south')


