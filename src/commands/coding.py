# Project: Akrios
# Filename: commands/coding.py
#
# Capability: admin
#
# Command Description: Allows an admin player to set a coding flag to indicate to others in
#                      the who listing that they are "afk coding"
#
# By: Jubelo

from commands import *

name = "coding"
version = 1

@Command(capability="admin")
def coding(caller, args):
    if caller.oocflags['coding'] == False:
        caller.oocflags['coding'] = True
        caller.write("You have been placed in coding mode.")
    else:
        caller.oocflags['coding'] = False
        caller.write('You have been removed from coding mode.')

