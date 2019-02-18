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
versin = 1

@Command(capability=["player", "mobile"])
def up(caller, args):
    Command.commandhash['move'](caller, 'up')


