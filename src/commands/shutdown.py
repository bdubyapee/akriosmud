#! usr/bin/env python3
# Project: Akrios
# filename: commands/shutdown.py
#
# Capability : admin
#
# Command Description: This command shuts down the game fully.
#
#
#
# By: Jubelo

from commands import *

name = "shutdown"
version = 1

requirements = {'capability': 'admin',
                'generic_fail': "See {WHelp shutdown{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def shutdown(caller, args):
    server.Server.done = True
