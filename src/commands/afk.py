#! /usr/bin/env python3
# Project: Akrios
# filename: commands/afk.py
#
# Capability: player
#
# Command Description: Away From Keyboard (AFK) toggler for player away
#                      indication to other players and self.
#
#
# By: Jubelo

from commands import *

name = "afk"
version = 1

@Command(capability='player')
def afk(caller, args):
    if caller.oocflags['afk'] == True:
        caller.oocflags['afk'] = False
        caller.write("AFK mode removed.")
    else:
        caller.oocflags['afk'] = True
        caller.write('You have been placed in AFK mode.')

