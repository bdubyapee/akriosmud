# Project: Akrios
# Filename: commands/longdescription.py
#
# Capability: player
#
# Command Description: Allows a player to set their short description
#
# By: Jubelo

from commands import *

name = "shortdescription"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp shortdescription{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def shortdescription(caller, args):
    args = args.split()
    if len(args) <= 0:
        caller.write("Please see {Whelp shortdescription{x for help.")
        return
    caller.short_description = ' '.join(args)[:80]
    caller.write('{xYour short description has been set.')

