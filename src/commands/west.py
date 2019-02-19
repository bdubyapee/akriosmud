# Project: Akrios
# Filename: commands/west.py
#
# Capability: player
#
# Command Description: Command to move a player west
#
# By: Jubelo

from commands import *

name = "west"
versin = 1

@Command(capability=["player", "mobile", "object"])
def west(caller, args):
    Command.commandhash['move'](caller, 'west')


