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
versin = 1

@Command(capability="player")
def southwest(caller, args):
    Command.commandhash['move'](caller, 'southwest')


