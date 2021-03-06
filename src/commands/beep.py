# Project: Akrios
# Filename: commands/beep.py
#
# Capability: player
#
# Command Description: Sends a beep command to another player to get their attention
#
# By: Jubelo

from commands import *

name = "beep"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp beep{x for help with this command.",
                'truth_checks':  [],
                'false_checks': [],
                'target': 'target_single_player_game_nopost'}


@Command(**requirements)
def beep(caller, args, **kwargs):
    target = kwargs['target']
    target.write(f"{{*\n\rYou have been paged by {caller.disp_name}")
    caller.write("They have been paged")

