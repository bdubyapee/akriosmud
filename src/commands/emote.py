# Project: Akrios
# Filename: commands/emote.py
#
# Capability: player
#
# Command Description: Allows a player to emote to the room, for RP.
#
# By: Jubelo

from commands import *

name = "emote"
version = 1


requirements = {'capability': 'player',
                'generic_fail': "See {WHelp emote{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': ['is_sleeping'],
                'target': 'target_all_player_room_post'}

@Command(**requirements)
def emote(caller, args, **kwargs):
    target_list = kwargs['target']
    args_ = kwargs['post']

    for person in target_list:
        if person == caller:
            prefix = ''
        else:
            prefix = '\n\r'
            
        name = caller.name_cap
        name = prefix + name
        person.write(f"\n\r{{g{name} {args_[:70]}{{x")


