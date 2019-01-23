#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/ooc.py
#
# Capability: player
#
# Command Description: This is the Out of Character (OOC) chat command. It is global, and not RP.
#
# By: Jubelo

from commands import *

name = "ooc"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp ooc{x for help with this command.",
                'truth_checks':  ['arg_required'],
                'false_checks': [],
                'target': 'target_all_player_game_post'}

@Command(**requirements)
def ooc(caller, args, **kwargs):
    target_list = kwargs['target']
    args_ = kwargs['post']
    for person in target_list:
        if person == caller:
            name = "You"
            plural = ''
        else:
            name = caller.name_cap
            plural = 's'
            name = '\n\r' + name
        person.write(f"{{B{name} OOC{plural}: '{args_[:300]}'{{x")


