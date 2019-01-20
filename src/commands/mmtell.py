#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/mmtell.py
#
# Capability: player
#
# Command Description: This is the tell command for the Gossip network. It goes
# to a player in another game.
#
# By: Jubelo

from commands import *

name = "mmtell"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp mmtell{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def mmtell(caller, args):
    if caller.oocflags_stored['mmchat'] == 'false':
        caller.write("You have that command self disabled with the 'toggle' command.")
        return

    if len(args.split()) == 0:
        caller.write("Did you have something to say or not?")
        return

    target = args.split()[0]
    if '@' in target:
        target, game = target.split('@')
    else:
        caller.write("Command format is 'mmtell player@game <message>'.")
        return

    message = args.split()[1:]

    message = ' '.join(message)

    if game.lower() in ['akrios', 'akriosmud']:
        caller.write("Just use in game channels to talk to players on Akrios.")
        return

    gossip.gsocket.msg_gen_player_tells(caller.name.capitalize(), game, target, message)

    
    caller.write(f"{{GYou MultiMUD tell {{y{target}@{game}{{x: '{{G{message}{{x'")

