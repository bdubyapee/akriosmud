#! usr/bin/env python3
# Project: Akrios
# filename: commands/__init__.py
#
# File Description: New commands package for handing executing "stuff" 
# any _thing_ needs to execute.
#
# By: Jubelo


import time
from functools import wraps
import os
import sys

sys.path.append('../')


import color
import area
import event
import exits
import gossip
import helpsys
import comm
import login
import races
import room
import player
import server
import world




# Basic truthfullness tests for command preparsing.

def is_standing(thing):
    fail_msg = "You cannot do that while standing."
    if hasattr(thing, "position") and thing.position == "standing":
        return (True, fail_msg)
    else:
        return (False, fail_msg)

def is_sitting(thing):
    fail_msg = "You cannot do that while sitting."
    if hasattr(thing, "position") and thing.position == "sitting":
        return (True, fail_msg)
    else:
        return (False, fail_msg)

def is_sleeping(thing):
    fail_msg = "You cannot do that while sleeping."
    if hasattr(thing, "position") and thing.position == "sleeping":
        return (True, fail_msg)
    else:
        return (False, fail_msg)

# Target verification / matching

def nospell_target_single_player_game_nopost(caller, args):
    args = args.lower()
    if args in player.playerlist_by_name:
        return (None, player.playerlist_by_name[args], None)
    else:
        return (None, False, None)

def nospell_target_single_player_game_post(caller, args):
    target, *args = args.split()
    target = target.lower()
    if target in player.playerlist_by_name and len(args) > 0:
        return (None, player.playerlist_by_name[target], ' '.join(args))
    else:
        return (None, False, None)

def nospell_target_single_player_room_post(caller, args):
    target, *args = args.split()
    target = target.lower()
    for eachthing in caller.location.contents:
        if eachthing.is_player and eachthing.name == target and len(args) > 0:
            return (None, player.playerlist_by_name[target], ' '.join(args))
    else:
        return (None, False, None)

def nospell_target_all_player_room_post(caller, args):
    target = [target for target in caller.location.contents if target.is_player]
    if len(target) > 0 and len(args) > 0:
        return (None, target, args)
    else:
        return (None, False, None)


class Command(object):
    commandhash = {}
    commandcapability = {}

    checks = {"is_standing": is_standing,
              "is_sitting": is_sitting,
              "is_sleeping": is_sleeping}

    targets = {"nospell_single_player_game_nopost": nospell_target_single_player_game_nopost,
               "nospell_single_player_game_post": nospell_target_single_player_game_post,
               "nospell_single_player_room_post": nospell_target_single_player_room_post,
               "nospell_all_player_room_post": nospell_target_all_player_room_post}

    def __init__(self, *args, **kwargs):
        self.dec_args = args
        self.dec_kwargs = kwargs

    def __call__(self, command):
        @wraps(command)
        def wrapped_f(*args, **kwargs):
            caller, args_ = args
            kwargs_ = kwargs

            if 'disabled' in self.dec_kwargs:
                caller.write("That command is disabled")
                return

            if self.dec_kwargs['capability'] not in caller.capability:
                caller.write("Huh?")
                return

            # If the command has target reqs perform those here, else write generic fail msg.
            if 'target' in self.dec_kwargs:
                spell, target, post = Command.targets[self.dec_kwargs['target']](caller, args_)

                if target == False:
                    if len(post) > 0:
                        caller.write("\n\rNot a valid target.")
                    if len(post) <= 0:
                        caller.write("\n\rArguments are required for this command.")
                    caller.write(self.dec_kwargs['generic_fail'])
                    return
                else:
                    kwargs_['spell'] = spell
                    kwargs_['target'] = target
                    kwargs_['post'] = post

            # Verify all checks that must be True are True
            if 'truth_checks' in self.dec_kwargs and len(self.dec_kwargs['truth_checks']) > 0:
                for eachcheck in self.dec_kwargs['truth_checks']:
                    if eachcheck in Command.checks:
                        true_false, msg = Command.checks[eachcheck](caller)
                        if true_false == False:
                            caller.write(msg)
                            return

            # Verify all checks that must be False are False
            if 'false_checks' in self.dec_kwargs and len(self.dec_kwargs['false_checks']) > 0:
                for eachcheck in self.dec_kwargs['false_checks']:
                    if eachcheck in Command.checks:
                        true_false, msg = Command.checks[eachcheck](caller)
                        if true_false == True:
                            caller.write(msg)
                            return
                
            try:
                command(caller, args_, **kwargs_)
            except Exception as err:
                to_log = (f"Error in command execution:\n\r"
                          f"Player: {caller.name}\n\r"
                          f"Command: {command}\n\r"
                          f"Args: {args_}\n\r"
                          f"KwArgs: {kwargs_}\n\r"
                          f"Error: {err}")
                comm.log(world.serverlog, f"\n\r{to_log}")
                caller.write("Something terrible has happened. Sorry!")
                return

        Command.commandhash[command.__name__] = wrapped_f
        Command.commandcapability[command.__name__] = self.dec_kwargs['capability']


# Admin Commands
from . import areaedit
from . import areastats
from . import coding
from . import dig
from . import exitedit
from . import helpedit
from . import playerinfo
from . import promote
from . import raceedit
from . import raceslist
from . import reload
from . import roomedit
from . import shutdown
from . import test_command
from . import viewolcdetails

# Player Commands
from . import afk
from . import alias
from . import arealist
from . import beep
from . import close
from . import commandslist
from . import down
from . import east
from . import emote
from . import goto
from . import help
from . import longdescription
from . import look
from . import mmchat
from . import mmtell
from . import move
from . import north
from . import northeast
from . import northwest
from . import ooc
from . import open
from . import prompt
from . import quit
from . import quote
from . import save
from . import say
from . import score
from . import shortdescription
from . import sit
from . import sleep
from . import south
from . import southeast
from . import southwest
from . import stand
from . import tell
from . import title
from . import toggle
from . import up
from . import west
from . import whisper
from . import who


