# Project: Akrios
# Filename: commands/emote.py
#
# Capability: player
#
# Command Description: Allows a player to emote to the room, for RP.
#
# By: Jubelo

from commands import *

name = "emote"
version = 1


requirements = {'capability': 'player',
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}

@Command(**requirements)
def emote(caller, args):
    if args == '':
        caller.write("See {Whelp emote{x for help with this command.")
        return
        
    for person in caller.location.contents:
        if person == caller:
            prefix = ''
        else:
            prefix = '\n\r'
            
        name = caller.name.capitalize()
        name = prefix + name
        person.write(f"{{g{name} {args[:170]}{{x")


