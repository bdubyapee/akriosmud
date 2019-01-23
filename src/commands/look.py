#! usr/bin/env python3
# Project: Akrios
# filename: commands/look.py
#
# Capability : player
#
# Command Description: The look command for players.
#
# By: Jubelo

from commands import *

name = "look"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp look{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}

@Command(**requirements)
def look(caller, args, **kwargs):
    if caller.location != 0 and len(args) <= 0:
        if caller.oocflags['viewOLCdetails'] == True:
            namepretext = f"{{W[{{xVNUM: {{B{caller.location.vnum}{{W]{{x "
            name = f"{namepretext}{{B{caller.location.name.capitalize()}{{x"
            theexits = []
            for key in caller.location.exits:
                destination = caller.location.exits[key].destination
                size = caller.location.exits[key].size
                theexits.append(f"{{C{key} {{W[{{xVNUM: {{B{destination}{{W] [{{G{size}{{W]{{x ")
            theexits = ', '.join(theexits)
        else:
            name = f"{{B{caller.location.name.capitalize()}{{x"
            theexits = ', '.join(caller.location.exits)

        desc = f"   {caller.location.description}"
        people = (person for person in caller.location.contents if person.is_player)
        
        if theexits == '':
            theexits = 'none'

        caller.write(f"\n\r{name}")
        caller.write(f"{desc}\n")
        caller.write(f"{{Y[{{GExits: {{B{theexits}{{Y]{{x")
        for dude in people:
            if dude is not caller and dude.name != '':
                if dude.oocflags['afk'] == True:
                    pretext = "{W[{RAFK{W]{x"
                else:
                    pretext = ""
                caller.write(f"   {pretext} {dude.name_cap} is {dude.position} here.")
    elif len(args) > 0:
        # Is it a room extra description?
        if args in caller.location.extradescriptions:
            caller.write(caller.location.extradescriptions[args])
            return
        # Is it a person?
        notfound = True
        lookingat = None
        if args == 'self':
            lookingat = caller
            notfound = False
        else:
            for person in caller.location.contents:
                if person.is_player and args in person.name:
                     lookingat = person
                     notfound = False
        if notfound == False:
            if lookingat.long_description == '':
                caller.write("They don't appear to have a description set yet.")
            else:
                caller.write(lookingat.long_description)
            caller.write("")
            caller.write("They are wearing:")
            caller.write("Nothing yet!")
            return
        caller.write("You don't see anything like that.")
        return
    else:
        caller.write("{xNowhere Special{x")
        caller.write("You see nothing in any direction.")
        caller.write("{{Y[{{GExits: {{Bnone{{Y]{{x")



