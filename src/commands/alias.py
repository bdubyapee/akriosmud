#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/alias.py
#
# Capability: player
#
# Command Description: A command which players can use to create an alias for another command.
#                      For example, they can alias 'n' to 'north' to use 'n' to execute 'north'.
#
#
# By: Jubelo

from commands import *

name = "alias"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp alias{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def alias(caller, args):
    args = args.split()
    if len(args) == 0:
        args.append('list')
    
    if args[0] == 'list':
        caller.write("Current alias' saved:")
        for one in caller.alias.keys():
            caller.write(f"{one} => {caller.alias[one]}")
    elif args[0] == 'remove' and len(args) == 2:
        if args[1] in caller.alias.keys():
            del caller.alias[args[1]]
            caller.write("Alias removed.")
        else:
            caller.write(f"No alias '{args[1]}' to remove.")
    elif args[0] == 'alias':
        caller.write("See {Whelp alias{x for help with this command.")
    else:
        caller.alias[args[0]] = ' '.join(args[1:])
        caller.write(f"Alias {args[0]} successfully created.")

