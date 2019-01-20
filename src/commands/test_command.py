#! usr/bin/env python3
# Project: Akrios
# filename: commands/test_command.py
#
# Capability : admin
#
# Command Description: Just a test command for playing with new ideas.
#
# By: Jubelo

from commands import *

name = 'test_command'
version = 1

requirements = {'capability': 'admin',
                'generic_fail': "See {WHelp test_command{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def test_command(caller, args, **kwargs):
    print(f"This is the command test_command executing with args {args} : kwargs {kwargs}")


