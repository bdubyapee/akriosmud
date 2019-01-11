# Project: Akrios
# Filename: commands/playerinfo.py
#
# Capability: admin
#
# Command Description: Allows admins to view additional details about players
#
# By: Jubelo

from commands import *

name = "playerinfo"
version = 1

@Command(capability="admin")
def playerinfo(caller, args):
    for person in player.playerlist:
        # This won't be called often, and it's a hell of a lot cleaner looking like this.
        name = person.name.capitalize()
        host = person.sock.host
        fileno = person.sock.socket.fileno()

        caller.write(f"Player: {name:15} Host: {host:15} {{R{fileno}{{x")


