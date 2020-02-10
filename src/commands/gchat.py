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

    channel, msg = args.split()
    channel = channel.lower()

    if channel not in grapevine.subscribed:
        caller.write("Channel not subscribed.\n\r{Wgchat <channel> <message>{x")
        caller.write(f"Subscribed channels are: {grapevine.subscribed}")
        return

    try:
        asyncio.create_task(grapevine.msg_gen_message_channel_send(caller, channel, msg))
    except:
        caller.write(f"{{WError chatting to Grapevine Network, try again later{{x")
        comm.wiznet(f"Error writing to Grapevine network. {caller.disp_name} : {msg}")
        return
    
    caller.write(f"{{GYou Grapevine {{B{channel}{{G chat{{x: '{{G{msg}{{x'")

    for eachplayer in player.playerlist:
        if eachplayer.oocflags_stored['grapevine'] == 'true' and eachplayer.aid != caller.aid:
            eachplayer.write(f"\n\r{{G{caller.disp_name} Grapevine {{B{channel}{{G chats{{x: '{{G{msg}{{x'")


