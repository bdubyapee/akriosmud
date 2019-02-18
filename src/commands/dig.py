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

requirements = {'capability': ['builder'],
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
            return
        else:
            targetvnum = int(args[1])
            if targetvnum in area.roomlist:
                caller.write(f"Room {{W{targetvnum}{{x already exists!")
                return
            if args[0] in caller.location.exits:
                caller.write("There is already an exit in that direction!")
                return

            newexitdata = {"direction": args[0],
                           "destination": targetvnum}
            revexitdata = {"direction": exits.oppositedirection[args[0]],
                           "destination": caller.location.vnum}

            newexitdataJSON = json.dumps(newexitdata, sort_keys=True, indent=4)
            revexitdataJSON = json.dumps(revexitdata, sort_keys=True, indent=4)

            myarea = caller.location.area
            if targetvnum < myarea.vnumlow or targetvnum > myarea.vnumhigh:
                caller.write("That vnum is not in this areas range!")
                return
            else:
                newroom = room.oneRoom(caller.location.area, vnum=targetvnum)
                area.roomlist[targetvnum] = newroom
                newroom.area.roomlist[targetvnum] = newroom
                exits.Exit(targetvnum, None, revexitdataJSON)
                exits.Exit(caller.location.vnum, None, newexitdataJSON)
                caller.write("")
    else:
        caller.write(helpstring)

