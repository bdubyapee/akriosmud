#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/gchat.py
#
# Capability: player
#
# Command Description: This is the Out of Character (OOC) chat command. It goes
# to the Grapevine MUD Chat Network.
#
# By: Jubelo

from commands import *

name = "gchat"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp gchat{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
def gchat(caller, args, **kwargs):
    if caller.oocflags_stored['grapevine'] == 'false':
        caller.write("You have Grapevine disabled with the 'toggle' command.")
        return

    if args.split()[0].lower() in grapevine.gsocket.subscribed:
        channel = args.split()[0].lower()
    else:
        caller.write("Channel not subscribed.\n\r{Wgchat <channel> <message>{x")
        caller.write(f"Subscribed channels are: {grapevine.gsocket.subscribed}")
        return

    try:
        grapevine.gsocket.msg_gen_message_channel_send(caller, channel, args)
    except:
        caller.write(f"{{WError chatting to Grapevine Network, try again later{{x")
        comm.wiznet(f"Error writing to Grapevine network. {caller.disp_name} : {args}")
        return
    
    caller.write(f"{{GYou Grapevine {{B{channel}{{x chat{{x: '{{G{args}{{x'")

    for eachplayer in player.playerlist:
        if eachplayer.oocflags_stored['grapevine'] == 'true' and eachplayer.aid != caller.aid:
            eachplayer.write(f"\n\r{{G{caller.disp_name} Grapevine {{B{channel}{{x chats{{x: '{{G{args}{{x'")


