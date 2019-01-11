# Project: Akrios
# Filename: commands/northwest.py
#
# Capability: player
#
# Command Description: Command to move a player northwest
#
# By: Jubelo

from commands import *

name = "northwest"
versin = 1

@Command(capability="player")
def northwest(caller, args):
    Command.commandhash['move'](caller, 'northwest')


