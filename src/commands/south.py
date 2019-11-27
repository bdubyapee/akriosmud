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
version = 1


@Command(capability=["player", "mobile", "object"])
def south(caller, args, **kwargs):
    Command.commandhash['move'](caller, 'south')
