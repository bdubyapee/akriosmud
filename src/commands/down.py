# Project: Akrios
# Filename: commands/down.py
#
# Capability: player
#
# Command Description: Command to move a player down
#
# By: Jubelo

from commands import *

name = "down"
versin = 1

@Command(capability=["player","mobile", "object"])
def down(caller, args):
    Command.commandhash['move'](caller, 'down')


