# Project: Akrios
# Filename: commands/longdescription.py
#
# Capability: player
#
# Command Description: Allows the player to set their long description
#
# By: Jubelo

from commands import *

name = "longdescription"
version = 1

@Command(capability="player")
def longdescription(caller, args):
    args = args.split()
    if len(args) <= 0:
        caller.write("Please see {Whelp longdescription{x for help.")
        return
    caller.long_description = ' '.join(args)[:2000]
    caller.write('{xYour description has been set.')

