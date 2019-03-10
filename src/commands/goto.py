# Project: Akrios
# Filename: commands/goto.py
#
# Capability: admin
#
# Command Description: Admin level command to "goto" any place or thing
#
# By: Jubelo

from commands import *

name = "goto"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp goto{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}

@Command(**requirements)
def goto(caller, args, **kwargs):
    args = args.split()
    try:
        vnum = int(args[0])
    except:
        vnum = None

    newroom = None

    if vnum is not None:
        newroom = area.room_by_vnum_global(vnum)

    if args[0].lower() in player.playerlist_by_name:
        newroom = player.playerlist_by_name[args[0].lower()].location

    if newroom == None:
        caller.write("That location doesn't appear to exist!")
    else:
        try:
            caller.move(newroom, caller.location, direction="goto")
        except:
            pass
        caller.interp("look")
        

