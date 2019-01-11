#! /usr/bin/env python3
# Project: Akrios
# filename: commands/toggle.py
#
# Capability: player
#
# Command Description: Allows toggling of flags and settings.
#
#
# By: Jubelo

from commands import *

name = "toggle"
version = 1

@Command(capability='player')
def toggle(caller, args):
    if args == 'newbie':
        if caller.oocflags_stored['newbie'] == 'true':
            caller.oocflags_stored['newbie'] = 'false'
            caller.write("{WNewbie Tip mode disabled.{x")
            caller.events.remove_event_type(eventtype="newbie tips")
        else:
            caller.oocflags_stored['newbie'] = 'true'
            caller.write('{WNewbie Tip mode enabled.{x')

            newevent = event.Event()
            newevent.owner = caller
            newevent.ownertype = 'player'
            newevent.eventtype = 'newbie tips'
            newevent.func = event.event_player_newbie_notify
            newevent.passes = 45 * event.PULSE_PER_SECOND
            newevent.totalpasses = newevent.passes
            caller.events.add(newevent)

    if args == 'mmchat':
        if caller.oocflags_stored['mmchat'] == 'true':
            caller.oocflags_stored['mmchat'] = 'false'
            caller.write("{WMultiMUD Chat disabled.{x")
        else:
            caller.oocflags_stored['mmchat'] = 'true'
            caller.write("{WMultiMUD Chat enabled.{x")


    if caller.oocflags_stored['newbie'] == 'true':
        newbie = "Enabled"
    else:
        newbie = "Disabled"

    if caller.oocflags_stored['mmchat'] == 'true':
        mmchat = "Enabled"
    else:
        mmchat = "Disabled"

    caller.write("Currently available settings to toggle:")
    caller.write(f"    {{Wnewbie{{x : {{R{newbie}{{x")
    caller.write(f"    {{Wmmchat{{x : {{R{mmchat}{{x")
