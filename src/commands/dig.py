# Project: Akrios
# Filename: commands/dig.py
#
# Capability: builder
#
# Command Description: Allows builder to "dig" to a new room which creates the exist and template.
#
# By: Jubelo

from commands import *

name = "dig"
version = 1

requirements = {'capability': 'builder',
                'generic_fail': "See {WHelp dig{x for help with this command.",
                'truth_checks':  ['is_standing', 'args_required'],
                'false_checks': []}

@Command(**requirements)
def dig(caller, args, **kwargs):
    helpstring = "Please see {Whelp dig{x for instructions."
    args = args.split()

    if args[0] in exits.directions:
        if len(args) != 2:
            caller.write(helpstring)
        else:
            targetvnum = int(args[1])
            if targetvnum in area.roomlist:
                caller.write(f"Room {{W{targetvnum}{{x already exists!")
                return
            if args[0] in caller.location.exits:
                caller.write("There is already an exit in that direction!")
                return
            defaultexitdata = "false 0 0 false 0 0 0 none huge false true none"
            newexitdata = f"{args[0]} {targetvnum} {defaultexitdata}"
            revexitdata = f"{exits.oppositedirection[args[0]]} {caller.location.vnum} {defaultexitdata}"
            myarea = caller.location.area
            if targetvnum < myarea.vnumlow or targetvnum > myarea.vnumhigh:
                caller.write("That vnum is not in this areas range!")
                return
            else:
                newroom = room.oneRoom(caller.location.area, vnum=targetvnum)
                area.roomlist[targetvnum] = newroom
                newroom.area.roomlist[targetvnum] = newroom
                newroom.exits[exits.oppositedirection[args[0]]] = exits.Exit(newroom, revexitdata)
                caller.location.exits[args[0]] = exits.Exit(caller.location, newexitdata)
    else:
        caller.write(helpstring)

