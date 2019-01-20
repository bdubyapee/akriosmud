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

requirements = {'capability': 'builder',
                'generic_fail': "See {WHelp raceslist{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
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

