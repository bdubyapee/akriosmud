# Project: Akrios
# Filename: commands/east.py
#
# Capability: player
#
# Command Description: Command to move a player east
#
# By: Jubelo

from commands import *

name = "east"
versin = 1

@Command(capability=["player", "mobile", "object"])
def east(caller, args):
    Command.commandhash['move'](caller, 'east')


