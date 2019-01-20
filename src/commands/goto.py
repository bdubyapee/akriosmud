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

requirements = {'capability': 'admin',
                'generic_fail': "See {WHelp goto{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def goto(caller, args):
    args = args.split()
    try:
        vnum = int(args[0])
    except:
        vnum = None
    newroom = None

    if vnum in area.roomlist.keys():
        newroom = area.roomByVnum(vnum)


    for oneplayer in player.playerlist:
        if oneplayer.name == args[0].lower():
            newroom = oneplayer.location


    if newroom == None:
        caller.write("That location doesn't appear to exist!")
    else:
        try:
            caller.move(newroom, caller.location, direction="goto")
        except:
            pass
        caller.interp("look")
        

