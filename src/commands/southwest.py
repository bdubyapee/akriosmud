# Project: Akrios
# Filename: commands/southwest.py
#
# Capability: player
#
# Command Description: Command to move a player southwest
#
# By: Jubelo

from commands import *

name = "southwest"
version = 1


@Command(capability=["player", "mobile", "object"])
def southwest(caller, args, **kwargs):
    Command.commandhash['move'](caller, 'southwest')
