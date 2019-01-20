# Project: Akrios
# Filename: commands/tell.py
#
# Capability: player
#
# Command Description: Sends a tell to another player.
#
# By: Jubelo

from commands import *

name = "tell"
version = 1


requirements = {'capability': 'player',
                'generic_fail' : "See {WHelp tell{x for help with this command.",
                'truth_checks':  [],
                'false_checks': [],
                'target': 'target_single_player_game_post'}

@Command(**requirements)
def tell(caller, args, **kwargs):
    target = kwargs['target']
    message = kwargs['post']
    target.write(f"\n\r{{y{caller.name_cap} tells you, '{message}'{{x.")
    caller.write(f"\n\r{{yYou tell {target.name_cap}, '{message}'{{x.")
