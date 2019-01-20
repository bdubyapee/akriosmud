# Project: Akrios
# Filename: commands/title.py
#
# Capability: player
#
# Command Description: Allows a player to modify their title for the "who" list.
#
# By: Jubelo

from commands import *

name = "title"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp title{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def title(caller, args):
    args = args.split()
    if len(args) == 0:
        caller.write("Please see {Whelp title{x for help.")
        return
    caller.title =  ' '.join(args)[0:40]
    caller.write('{xYour title has been set.')

