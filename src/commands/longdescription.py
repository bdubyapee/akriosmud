# Project: Akrios
# Filename: commands/longdescription.py
#
# Capability: player
#
# Command Description: Allows the player to set their long description
#
# By: Jubelo

from commands import *

name = "longdescription"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp longdescription{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
def longdescription(caller, args, **kwargs):
    formatter = textwrap.TextWrapper(width=76)
    formatted_text = formatter.wrap(args[:2000])
    caller.long_description = '\n'.join(formatted_text)

    caller.write('{xYour description has been set.')

