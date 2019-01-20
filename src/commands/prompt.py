# Project: Akrios
# Filename: commands/prompt.py
#
# Capability: player
#
# Command Description: Allows the player to modify their prompt
#
# By: Jubelo

from commands import *

name = "prompt"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp prompt{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def prompt(caller, args):
    args = args.split()
    if len(args) == 0:
        caller.write("Please see {Whelp prompt{x for help.")
        return
    
    caller.prompt = ' '.join(args[:50])
    caller.write('{xYour prompt has been configured.')

