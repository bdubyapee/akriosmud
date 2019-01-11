# Project: Akrios
# filename: commands/viewolcdetails.py
#
# Capabilities: builder
#
# Command Description: This flag turns on and allows the builder+ capability user to see inline details.
#
# By: Jubelo

from commands import *

name = "viewolcdetails"
version = 1

@Command(capability='builder')
def viewolcdetails(caller, args):
    if caller.oocflags['viewOLCdetails'] == True:
        caller.oocflags['viewOLCdetails'] = False
        caller.write("You will no longer see OLC details.")
    else:
        caller.oocflags['viewOLCdetails'] = True
        caller.write("You will now see OLC details.")


