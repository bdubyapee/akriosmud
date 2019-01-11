# Project: Akrios
# Filename: commands/commandlist.py
#
# Capability: player
#
# Command Description: Listing of currently avaiable commands filtered by capabilities.
#
# By: Jubelo

from commands import *

name = "commandslist"
version = 1

@Command(capability="player")
def commandslist(caller, args):

    commandhash = Command.commandhash
    commandcapability = Command.commandcapability

    header = f"{{rCommands Available{{x"
    caller.write(f"{header:^80}")
    caller.write("")
    sub_header = f"{{BPlease see {{Whelp <command>{{B for additional information{{x"
    caller.write(f"{sub_header:^80}")
    caller.write("")
    retval = []
    
    for comm in commandhash.keys():
        if commandcapability[comm] in caller.capability:
            retval.append(comm)
    
    retval.sort()
    numcols = 4
    while (len(retval) % numcols) > 0:
        retval.append(' ')
    for i in range(0, len(retval), numcols):
        output = ''
        for l in range(0, numcols):
            output += f"{retval[i+l]:20}"
        caller.write(output)

    caller.write("")
    caller.write("\n\r{WUsage{x: <command> <optional arguments>")
