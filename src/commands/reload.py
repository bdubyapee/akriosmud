#! /usr/bin/env python3
# Project: Akrios
# filename: commands/reload.py
#
# Capability: admin
#
# Command Description: place holder for a reload of commands to trigger
#
#
# By: Jubelo

from commands import *

name = "reload"
version = 1

requirements = {'capability': 'admin',
                'generic_fail': "See {WHelp reload{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def reload(caller, args):
    caller.write("We'll never make it to this line")

