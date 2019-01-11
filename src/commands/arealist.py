# Project: Akrios
# Filename: commands/arealist.py
#
# Capability: player
#
# Command Description: Provides the player with a list of areas
#
# By: Jubelo

from commands import *

name = "arealist"
version = 1

@Command(capability="player")
def arealist(caller, args):
    
    if caller.is_deity or caller.is_builder or caller.is_admin:
        see_vnums = True
    else:
        see_vnums = False
    for eacharea in area.arealist:
        # This won't be called that often, looks cleaner this way. Can reevaluate later.
        vnum_string = ""
        if see_vnums:
            vnum_string = f"{{W[{{B{eacharea.vnumlow:<6} - {eacharea.vnumhigh:>6}{{W]{{x  "
        name = eacharea.name.capitalize()
        diff = eacharea.difficulty.capitalize()

        caller.write(f"{vnum_string}{{W[ {{B{diff:<8}{{W ]{{x {name}")
    caller.write("")

