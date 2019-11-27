# Project: Akrios
# Filename: commands/northeast.py
#
# Capability: player
#
# Command Description: Command to move a player northeast
#
# By: Jubelo

from commands import *

name = "northeast"
version = 1


@Command(capability=["player", "mobile", "object"])
def northeast(caller, args, **kwargs):
    Command.commandhash['move'](caller, 'northeast')
