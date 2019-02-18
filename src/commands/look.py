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

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp look{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}

@Command(**requirements)
def look(caller, args, **kwargs):
    if caller.location != 0 and len(args) <= 0:
        if caller.is_player and caller.oocflags['viewOLCdetails'] == True:
            namepretext = f"{{W[{{xVNUM: {{B{caller.location.vnum}{{W]{{x "
            name = f"{namepretext}{{B{caller.location.name}{{x"
            theexits = []
            for key in caller.location.exits:
                destination = caller.location.exits[key].destination
                size = caller.location.exits[key].size
                theexits.append(f"{{C{key} {{W[{{xVNUM: {{B{destination}{{W] [{{G{size}{{W]{{x ")
            theexits = ', '.join(theexits)
        else:
            name = f"{{B{caller.location.name}{{x"
            theexits = ', '.join(caller.location.exits)

        desc = f"   {caller.location.description}"
        things = (thing for thing in caller.location.contents)
        
        if theexits == '':
            theexits = 'none'

        caller.write(f"\n\r{name}")
        caller.write(f"{desc}\n")
        caller.write(f"{{Y[{{GExits: {{B{theexits}{{Y]{{x")
        for thing in things:
            if thing is not caller and thing.name != '':
                if thing.is_player and thing.oocflags['afk'] == True:
                    pretext = "{W[{RAFK{W]{x"
                else:
                    pretext = ""

                if thing.is_player:
                    caller.write(f"   {pretext} {thing.name_cap} is {thing.position} here.")
                elif thing.is_mobile:
                    caller.write(f"   {pretext} {thing.short_description} is {thing.position} here.")
                elif thing.is_object:
                    caller.write(f"   {pretext} {thing.short_description} is here.")
              
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
            for thing in caller.location.contents:
                if hasattr(thing, "name"):
                    if args in thing.name:
                        lookingat = thing
                        notfound = False
                if hasattr(thing, "keywords"):
                    if args in thing.keywords:
                        lookingat = thing
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



