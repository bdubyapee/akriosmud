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

requirements = {'capability': 'admin',
                'generic_fail': "See {WHelp playerinfo{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def playerinfo(caller, args):
    for person in player.playerlist:
        name = person.name_cap
        host = person.sock.host
        fileno = person.sock.socket.fileno()

        caller.write(f"Player: {name:15} Host: {host:15} {{R{fileno}{{x")


