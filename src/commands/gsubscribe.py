#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/gsubscribe.py
#
# Capability: player
#
# Command Description: Used to subscribe or unsubscribe from Grapevine Channels.
#
# By: Jubelo

from commands import *

name = "gsubscribe"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp gsubscribe{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
def gsubscribe(caller, args='', **kwargs):
    if caller.oocflags_stored['grapevine'] == 'false':
        caller.write("You have Grapevine disabled with the 'toggle' command.")
        return

    if args == '':
        caller.write(f"Akrios subscribed to: {grapevine.gsocket.subscribed}.")
        caller.write(f"You are subscribed to: {caller.oocflags['grapevine_channels']}.")
        return

    if ' ' in args:
        channel, force_ = args.split()
        channel = channel.lower()
        force_ = force_.lower()
    else:
        channel = args.lower()
        force_ = ''

    if caller.is_admin and force_ == 'force':
        if channel in grapevine.gsocket.subscribed:
            grapevine.gsocket.msg_gen_chan_unsubscribe(channel)
            caller.write(f"Sending unsubscribe to Grapevine for channel: {channel}")
            return
        else:
            grapevine.gsocket.msg_gen_chan_subscribe(channel)
            caller.write(f"Sending subscribe to Grapevine for channel: {channel}")
            return

    if channel in grapevine.gsocket.subscribed:
        if channel in caller.oocflags['grapevine_channels']:
            caller.write(f"You are already subscribed to channels: {caller.oocflags['grapevine_channels']}.")
            return
        else:
            caller.oocflags['grapevine_channels'].append(channel)
            caller.write(f"Subscribing you to {channel}")
    else:
        caller.write("Akrios is not subscribed to that Grapevine channel.  Ask Jubelo to subscribe.")
