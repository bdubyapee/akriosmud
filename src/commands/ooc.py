#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/ooc.py
#
# Capability: player
#
# Command Description: This is the Out of Character (OOC) chat command. It is global, and not RP.
#
# By: Jubelo

from commands import *

name = "ooc"
version = 1

@Command(capability="player")
def ooc(caller, args):
    if len(args.split()) == 0:
        caller.write("Did you have something to say or not?")
        return
 
    for person in player.playerlist:
        if person == caller:
            name = "You"
            plural = ''
        else:
            name = caller.name.capitalize()
            plural = 's'
            name = '\n\r' + name
        person.write(f"{{B{name} OOC{plural}: '{args[:300]}'{{x")


