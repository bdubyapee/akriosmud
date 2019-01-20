# Project: Akrios
# Filename: commands/say.py
#
# Capability: player
#
# Command Description: Allows the player to say something to the room they are in.
#
# By Jubelo

from commands import *

name = "say"
version = 1


requirements = {'capability': 'player',
                'generic_fail': "See {WHelp say{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping'],
                'target': 'nospell_all_player_room_post'}

@Command(**requirements)
def say(caller, args, **kwargs):
    target_list = kwargs['target']
    message = kwargs['post']
        
    for person in target_list:
        if person == caller:
            name = "You"
            plural = ''
        else:
            name = caller.name_cap
            plural = 's'
            name = '\n\r' + name
        person.write(f"{{c{name} say{plural}, '{args[:300]}'{{x")

