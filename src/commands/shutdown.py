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

@Command(capability='admin')
def shutdown(caller, args):
    server.Server.done = True
