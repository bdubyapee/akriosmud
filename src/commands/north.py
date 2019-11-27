# Project: Akrios
# Filename: commands/north.py
#
# Capability: player
#
# Command Description: Command to move a player north
#
# By: Jubelo

from commands import *

name = "north"
version = 1


@Command(capability=["player", "mobile", "object"])
def north(caller, args, **kwargs):
    Command.commandhash['move'](caller, 'north')
