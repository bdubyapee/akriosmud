#! usr/bin/env python3
# Project: Akrios
# filename: commands/__init__.py
#
# File Description: New commands package for handing executing "stuff" 
# any _thing_ needs to execute.
#
# By: Jubelo


from functools import wraps
import json
import os
import sys
import textwrap
import time
import uuid

sys.path.append('../')


import area
import color
import comm
import event
import exits
import grapevine
import helpsys
import login
import mobile
import player
import races
import room
import server
import world


# Basic truthfullness tests for command preparsing.

def args_required(thing, args, **kwargs):
    fail_msg = kwargs['generic_fail']
    if len(args.split()) > 0:
        return (True, fail_msg)
    else:
        return (False, fail_msg)

def is_standing(thing, args, **kwargs):
    fail_msg = "You cannot do that while standing."
    if hasattr(thing, "position") and thing.position == "standing":
        return (True, fail_msg)
    else:
        return (False, fail_msg)

def is_sitting(thing, args, **kwargs):
    fail_msg = "You cannot do that while sitting."
    if hasattr(thing, "position") and thing.position == "sitting":
        return (True, fail_msg)
    else:
        return (False, fail_msg)

def is_sleeping(thing, args, **kwargs):
    fail_msg = "You cannot do that while sleeping."
    if hasattr(thing, "position") and thing.position == "sleeping":
        return (True, fail_msg)
    else:
        return (False, fail_msg)

# Target verification / matching

def target_single_player_game_nopost(caller, args):
    '''
        Expect: target
        Target must be a player, can be anywhere in game, no post target args.
    '''
    args = args.lower()
    if args in player.playerlist_by_name:
        return (player.playerlist_by_name[args], None)
    else:
        return (False, None)

def target_single_player_game_post(caller, args):
    '''
        Expect: target <one or more character/words args>
        Target must be a player, can be anywhere in game, must have arguments.
    '''
    target, *args = args.split()
    target = target.lower()
    if target in player.playerlist_by_name and len(args) > 0:
        return (player.playerlist_by_name[target], ' '.join(args))
    elif len(args) <= 0:
        return (False, False)
    else:
        return (False, None)

def target_single_player_room_nopost(caller, args):
    '''
        Expect: target
        Target must be a player, must be in same room as caller, no post target args.
    '''
    args = args.lower()
    if args in player.playerlist_by_name:
        if player.playerlist_by_name[args].location == caller.location:
            return (player.playerlist_by_name[args], None)
    else:
        return (False, None)

def target_single_player_room_post(caller, args):
    '''
        Expect: target <one or more character/words args>
        Target must be a player, must be in same room as caller, must have argumnets.
    '''
    target, *args = args.split()
    target = target.lower()

    if len(args) <= 0:
        return (False, False)

    for eachthing in caller.location.contents:
        if eachthing.is_player and eachthing.name == target and len(args) > 0:
            return (player.playerlist_by_name[target], ' '.join(args))
        
    return (False, None)

def target_single_thing_room_nopost(caller, args):
    '''
        Expect: target
        Target must be a thing, must be in same room as caller, no post target args.
    '''
    target = args.lower()

    for eachthing in caller.location.contents:
        name = eachthing.disp_name.lower()
        if name.startswith(target):
            return (eachthing, one)
        elif hasattr(eachthing, "keywords"):
            for eachkw in eachthing.keywords:
                if eachkw.startswith(target):
                    return (eachthing, None)

    return (False, None)

def target_single_thing_room_post(caller, args):
    '''
        Expect: target <one or more character/words args>
        Target must be a thing, must be in same room as caller, must have argumnets.
    '''
    target, *args = args.split()
    target = target.lower()

    if len(args) <= 0:
        return (False, False)

    for eachthing in caller.location.contents:
        name = eachthing.disp_name.lower()
        if name.startswith(target) and len(args) > 0:
            return (eachthing, ' '.join(args))

    return (False, None)

def target_all_player_room_nopost(caller, args):
    '''
        Expect: 
        Target will be all players in same room as caller, no post target args.
    '''
    target = [target for target in caller.location.contents if target.is_player]
    if len(target) > 0:
        return (target, None)
    else:
        return (False, None)

def target_all_player_room_post(caller, args):
    '''
        Expect: <one or more character/words args>
        Target will be all players in same room as caller, must have arguments.
    '''
    if len(args) <= 0:
        return (False, False)

    target = [target for target in caller.location.contents if target.is_player]
    if len(target) > 0 and len(args) > 0:
        return (target, args)
    else:
        return (False, None)

def target_all_things_room_nopost(caller, args):
    '''
        Expect: 
        Target will be all things in same room as caller, no arguments required.
    '''
    return (caller.location.contents, None)

def target_all_things_room_post(caller, args):
    '''
        Expect: <one or more character/words args>
        Target will be all things in same room as caller, arguments are required.
    '''
    if len(args) <= 0:
        return (False, False)
   
    return (caller.location.contents, args)
    

def target_all_player_game_post(caller, args):
    '''
        Expect: <one or more character/words args>
        Target will be all players in the game, arguments are required.
    '''
    if len(args) <= 0:
        return (False, False)

    return (player.playerlist, args)


class Command(object):
    commandhash = {}
    commandcapability = {}

    checks = {"args_required": args_required,
              "is_standing": is_standing,
              "is_sitting": is_sitting,
              "is_sleeping": is_sleeping}

    targets = {"target_single_player_game_nopost": target_single_player_game_nopost,
               "target_single_player_game_post": target_single_player_game_post,
               "target_single_player_room_nopost": target_single_player_room_nopost,
               "target_single_player_room_post": target_single_player_room_post,
               "target_single_thing_room_nopost": target_single_thing_room_nopost,
               "target_single_thing_room_post": target_single_thing_room_post,
               "target_all_player_room_nopost": target_all_player_room_nopost,
               "target_all_player_room_post": target_all_player_room_post,
               "target_all_things_room_nopost": target_all_things_room_nopost,
               "target_all_things_room_post": target_all_things_room_post,
               "target_all_player_game_post": target_all_player_game_post}

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

            if not set(self.dec_kwargs['capability']) & set(caller.capability):
                caller.write("Huh?")
                return
            #if self.dec_kwargs['capability'] not in caller.capability:
            #    caller.write("Huh?")
            #    return

            # If the command has target requirements perform those here.
            if 'target' in self.dec_kwargs:
                target, post = Command.targets[self.dec_kwargs['target']](caller, args_)

                if target == False and post is None:
                    caller.write("\n\rNot a valid target.")
                    caller.write(self.dec_kwargs['generic_fail'])
                    return
                elif post is False:
                    caller.write("\n\rArguments are required for this command.")
                    caller.write(self.dec_kwargs['generic_fail'])
                    return
                else:
                    kwargs_['target'] = target
                    kwargs_['post'] = post

            # Verify all checks that must be True are True
            if 'truth_checks' in self.dec_kwargs and len(self.dec_kwargs['truth_checks']) > 0:
                for eachcheck in self.dec_kwargs['truth_checks']:
                    if eachcheck in Command.checks:
                        true_false, msg = Command.checks[eachcheck](caller, args_, **self.dec_kwargs)
                        if true_false == False:
                            caller.write(msg)
                            return

            # Verify all checks that must be False are False
            if 'false_checks' in self.dec_kwargs and len(self.dec_kwargs['false_checks']) > 0:
                for eachcheck in self.dec_kwargs['false_checks']:
                    if eachcheck in Command.checks:
                        gen_fail = self.dec_kwargs['generic_fail']
                        true_false, msg = Command.checks[eachcheck](caller, args_, **self.dec_kwargs)
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
from . import force
from . import grestart
from . import helpedit
from . import playerinfo
from . import promote
from . import raceedit
from . import raceslist
from . import roomedit
from . import shutdown
from . import viewolcdetails

# Player Commands
from . import afk
from . import alias
from . import arealist
from . import beep
from . import close
from . import commandslist
from . import down
from . import drop
from . import east
from . import emote
from . import get
from . import goto
from . import help
from . import inventory
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


