# Project: Akrios
# Filename: commands/quote.py
#
# Capability: player
#
# Command Description: Allows the player to send a quote game wide
#
# By Jubelo

from commands import *

name = "quote"
version = 1

@Command(capability="player")
def quote(caller, args):
    if len(args.split()) == 0:
        caller.write("Did you have something to quote or not?")
        return
    
    for person in player.playerlist:
        if person == caller:
            name = "You"
            plural = ''
        else:
            name = caller.name.capitalize()
            plural = 's'
            name = '\n\r' + name
        person.write(f"{{y{name} Quote{plural}: '{args[:300]}'{{x")

