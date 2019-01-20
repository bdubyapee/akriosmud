# Project: Akrios
# Filename: commands/whisper.py
#
# Capability: player
#
# Command Description: Allows the player to whisper something to a player in the room they are in.
#
# By Jubelo

from commands import *

name = "whisper"
version = 1


requirements = {'capability': 'player',
                'generic_fail': "See {WHelp whisper{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping'],
                'target': 'nospell_single_player_room_post'}

@Command(**requirements)
def whisper(caller, args):
    target = kwargs['target']
    message = kargs['post']
    target.write(f"\n\r{{g{caller.name_cap} whispers to you, '{message}'{{x.")
    caller.write(f"\n\r{{gYou whisper to {target.name_cap}, '{message}'{{x.")

