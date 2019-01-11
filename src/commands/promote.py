# Project: Akrios
# Filename: commands/promote.py
#
# Capability: admin
#
# Command Description: Allows an Admin to promote another user to a specific capabilities profile.
#
# By: Jubelo

from commands import *

name = "promote"
version = 1

@Command(capability="admin")
def promote(caller, args):
    args = args.split()
    target = None
    
    if len(args) != 2:
        caller.write("See {Whelp promote{x for assistance.")
        return
        
    if args[1] not in ['admin', 'builder', 'deity']:
        caller.write("That is not a valid promotion option.")
        return
    
    for oneplayer in player.playerlist:
        if oneplayer.name == args[0]:
            target = oneplayer

    if target == None:
        caller.write("I can't find that player.")
        return
            
    if 'admin' in args[1] and 'admin' not in target.capability:
        target.capability.append('admin')
        target.write("You've been promoted to Admin status!")
        status = 'admin'
    if 'builder' in args[1] and 'builder' not in target.capability:
        target.capability.append('builder')
        target.write("You've been promoted to Builder status!")
        status = 'builder'
    if 'deity' in args[1] and 'deity' not in target.capability:
        target.capability.append('deity')
        target.write("You've been promoted to Deity status!")
        status = 'deity'
    target.save()
    caller.write(f"You have promoted {target.name} to {status} status!")


