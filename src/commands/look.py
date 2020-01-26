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
        if caller.is_player and caller.oocflags['viewOLCdetails'] is True:
            namepretext = f"{{W[{{xVNUM: {{B{caller.location.vnum}{{W]{{x "
            name_ = f"{namepretext}{{B{caller.location.name}{{x"
            theexits = []
            for key in caller.location.exits:
                destination = caller.location.exits[key].destination
                size = caller.location.exits[key].size
                theexits.append(f"{{C{key} {{W[{{xVNUM: {{B{destination}{{W] [{{G{size}{{W]{{x ")
            theexits = ', '.join(theexits)
        else:
            name_ = f"{{B{caller.location.name}{{x"
            theexits = ', '.join(caller.location.exits)

        desc = f"   {caller.location.description}"
        things = (thing for thing in caller.location.contents)
        
        if theexits == '':
            theexits = 'none'

        caller.write(f"\n\r{name_}")
        caller.write(f"{desc}\n")
        caller.write(f"{{Y[{{GExits: {{B{theexits}{{Y]{{x")
        for thing in things:
            if thing is not caller and thing.name:
                if thing.is_player and thing.oocflags['afk'] == True:
                    pretext = "{W[{RAFK{W]{x"
                else:
                    pretext = ""

                if thing.is_player or thing.is_mobile:
                    caller.write(f"   {pretext} {thing.disp_name} is {thing.position} here.")
                else:
                    caller.write(f"   {pretext} {thing.disp_name} is here.")
              
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
                    if args.lower() in thing.name:
                        lookingat = thing
                        notfound = False
                if hasattr(thing, "keywords"):
                    if args.lower() in thing.keywords:
                        lookingat = thing
                        notfound = False
        if notfound is False:
            if not lookingat.long_description:
                caller.write("They don't appear to have a description set yet.")
            else:
                caller.write(lookingat.long_description)
            caller.write("")
            if lookingat.is_player or lookingat.is_mobile:
                caller.write("They are wearing:")

                for each_loc, each_aid in lookingat.equipped.items():
                    if lookingat.equipped[each_loc] is None:
                        eq_name = "nothing"
                    else:
                        eq_name = lookingat.contents[each_aid].disp_name

                    preface = "worn on "
                    if each_loc == "floating nearby":
                        preface = ""
                    if 'hand' in each_loc:
                        preface = "held in "
                    if each_loc in ["neck", "waist"]:
                        preface = "worn around "
                    each_loc = f"{preface}{each_loc}"

                    caller.write(f"  <{each_loc:22}>   {eq_name:40}")
            caller.write("")
            return

        caller.write("You don't see anything like that.")
    else:
        caller.write("{xNowhere Special{x")
        caller.write("You see nothing in any direction.")
        caller.write("{{Y[{{GExits: {{Bnone{{Y]{{x")



