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
import logging

log = logging.getLogger(__name__)

name = "toggle"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp toggle{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
def toggle(caller, args):
    if args == 'newbie':
        if caller.oocflags_stored['newbie'] == 'true':
            caller.oocflags_stored['newbie'] = 'false'
            caller.write("\n\r{WNewbie Tip mode disabled.{x")
            caller.events.remove_event_type(eventtype="newbie tips")
        else:
            caller.oocflags_stored['newbie'] = 'true'
            caller.write('\n\r{WNewbie Tip mode enabled.{x')

            newevent = event.Event()
            newevent.owner = caller
            newevent.ownertype = 'player'
            newevent.eventtype = 'newbie tips'
            newevent.func = event.event_player_newbie_notify
            newevent.passes = 45 * event.PULSE_PER_SECOND
            newevent.totalpasses = newevent.passes
            caller.events.add(newevent)

    if args == 'grapevine':
        if caller.oocflags_stored['grapevine'] == 'true':
            caller.oocflags_stored['grapevine'] = 'false'
            caller.write("\n\r{WGrapevine System disabled.{x")
        else:
            caller.oocflags_stored['grapevine'] = 'true'
            caller.write("\n\r{WGrapevine System enabled.{x")

    if args == 'ooc':
        if caller.oocflags_stored['ooc'] == 'true':
            caller.oocflags_stored['ooc'] = 'false'
            caller.write("\n\r{WOOC Channel disabled.{x")
        else:
            caller.oocflags_stored['ooc'] = 'true'
            caller.write("\n\r{WOOC Channel enabled.{x")

    if args == 'quote':
        if caller.oocflags_stored['quote'] == 'true':
            caller.oocflags_stored['quote'] = 'false'
            caller.write("\n\r{WQuote Channel disabled.{x")
        else:
            caller.oocflags_stored['quote'] = 'true'
            caller.write("\n\r{WQuote Channel enabled.{x")

    if caller.is_admin:
        if args == 'log debug':
            if logging.getLevelName(logging.root.getEffectiveLevel()) == "INFO":
                logging.root.setLevel("DEBUG")
                log.warning(f"{caller.name.capitalize()} Changed log level to DEBUG")
                caller.write("\n\r{WSystem level debug has been enabled.{x")
            else:
                logging.root.setLevel("INFO")
                log.warning(f"{caller.name.capitalize()} Changed log level to INFO")
                caller.write("\n\r{WSystem level debug has been disabled.{x")

    if caller.oocflags_stored['newbie'] == 'true':
        newbie_ = "Enabled"
    else:
        newbie_ = "Disabled"

    if caller.oocflags_stored['grapevine'] == 'true':
        grapevine_ = "Enabled"
    else:
        grapevine_ = "Disabled"

    if caller.oocflags_stored['ooc'] == 'true':
        ooc_ = "Enabled"
    else:
        ooc_ = "Disabled"

    if caller.oocflags_stored['quote'] == 'true':
        quote_ = "Enabled"
    else:
        quote_ = "Disabled"

    caller.write("\n\rCurrently available settings to toggle:")
    caller.write(f"    {{Wnewbie{{x : {{R{newbie_}{{x")
    caller.write(f"    {{Wgrapevine{{x : {{R{grapevine_}{{x")
    caller.write(f"    {{Wooc{{x    : {{R{ooc_}{{x")
    caller.write(f"    {{Wquote{{x  : {{R{quote_}{{x")
    caller.write(f"")
    if caller.is_admin:
        caller.write(f"    {{Wlog debug{{x : {{R{logging.getLevelName(log.getEffectiveLevel())}{{x")
