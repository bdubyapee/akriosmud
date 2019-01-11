# Project: Akrios
# Filename: commands/southeast.py
#
# Capability: player
#
# Command Description: Command to move a player southeast
#
# By: Jubelo

from commands import *

name = "southeast"
versin = 1

@Command(capability="player")
def southeast(caller, args):
    Command.commandhash['move'](caller, 'southeast')


