# Project: Akrios
# Filename: commands/quote.py
#
# Capability: player
#
# Command Description: Allows the player to send a quote game wide
#
# By Jubelo

from commands import *

name = "quote"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp quote{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': [],
                'target': 'target_all_player_game_post'}

@Command(**requirements)
def quote(caller, args, **kwargs):
    if caller.oocflags_stored['quote'] == 'false':
        caller.write("You have the Quote channel disabled. Use the {Wtoggle{x command to enable it.")
        return

    target_list = kwargs['target']
    args_ = kwargs['post']
    
    for person in target_list:
        if person.oocflags_stored['quote'] == 'false':
            continue
        if person == caller:
            name = "You"
            plural = ''
        else:
            name = caller.name_cap
            plural = 's'
            name = '\n\r' + name
        person.write(f"{{y{name} Quote{plural}: '{args_[:300]}'{{x")

