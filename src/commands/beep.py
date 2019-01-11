# Project: Akrios
# Filename: commands/beep.py
#
# Capability: player
#
# Command Description: Seends a beep command to another player to get their attention
#
# By: Jubelo

from commands import *

name = "beep"
version = 1

@Command(capability="player")
def beep(caller, args):
    if len(args.split()) == 0:
        caller.write("See {Whelp beep{x for help with this command.")
        return
    else:
        for person in player.playerlist:
            if person.name in args.lower():
                person.sock.send(b'\x07')
                person.write(f"\n\rYou have been paged by {caller.name.capitalize()}.")
                caller.write("They have been paged.")
                return
        caller.write("That person cannot be located")


