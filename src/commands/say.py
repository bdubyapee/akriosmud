# Project: Akrios
# Filename: commands/say.py
#
# Capability: player
#
# Command Description: Allows the player to say something to the room they are in.
#
# By Jubelo

from commands import *

name = "say"
version = 1

@Command(capability="player")
def say(caller, args):
    args = args.split()
    if len(args) <= 0:
        caller.write("Did you have something to say or not?")
        return
        
    for person in caller.location.contents:
        if person == caller:
            name = "You"
            plural = ''
        else:
            name = caller.name.capitalize()
            plural = 's'
            name = '\n\r' + name
        person.write(f"{{c{name} say{plural}, '{' '.join(args[:300])}'{{x")

