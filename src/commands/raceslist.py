# Project: Akrios
# Filename: commands/raceslist.py
#
# Capability: builder
#
# Command Description: Provides a list of all of the races for builders as a reference.
#
# By: Jubelo

from commands import *

name = "raceslist"
version = 1

@Command(capability="builder")
def raceslist(caller, args):
    caller.write("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=Races=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    caller.write("")
    retval = []
    for arace in races.racesdict.keys():
        retval.append(races.racesdict[arace].name.capitalize())
    retval.sort()
    numcols = 6
    while (len(retval) % numcols) > 0:
        retval.append(' ')
    for i in range(0, len(retval), numcols):
        output = ''
        for l in range(0, numcols):
            output += f"{retval[i+l]:12}"
        caller.write(output)

