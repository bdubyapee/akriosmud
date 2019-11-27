# Project: Akrios
# Filename: commands/up.py
#
# Capability: player
#
# Command Description: Command to move a player up
#
# By: Jubelo

from commands import *

name = "up"
version = 1


@Command(capability=["player", "mobile", "object"])
def up(caller, args, **kwargs):
    Command.commandhash['move'](caller, 'up')
