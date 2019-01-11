#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/save.py
#
# Capability : player
#
# Command Description: This command saves the player data to disk immediatly.
#
# By: Jubelo

from commands import *

name = "save"
version = 1

@Command(capability='player')
def save(caller, args):
    caller.save()
    caller.write("Saved.  Your character is also autosaved every 5 minutes.")


