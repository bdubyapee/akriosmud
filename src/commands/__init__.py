#! usr/bin/env python3
# Project: Akrios
# filename: commands/__init__.py
#
# File Description: New commands package for handing executing "stuff" 
# any _thing_ needs to execute.
#
# By: Jubelo


import time
from functools import wraps
import os
import sys

sys.path.append('../')


import color
import area
import event
import exits
import gossip
import helpsys
import comm
import login
import races
import room
import player
import server
import world



class Command(object):
    # Dictionary for each command mapping 'stringname' : func()
    commandhash = {}
    # Dictionary for each command mapping 'stringname' : 'capability'
    commandcapability = {}

    def __init__(self, *args, **kwargs):
        self.decorator_args = args
        self.decorator_kwargs = kwargs

    def __call__(self, command):
        @wraps(command)
        def wrapped_f(*args, **kwargs):
            caller, _args = args
            if self.decorator_kwargs['capability'] in caller.capability:
                command(caller, _args, **kwargs)
            elif 'disabled' in kwargs:
                caller.write("That command is disabled")
            else:
                caller.write("Huh?")
        Command.commandhash[command.__name__] = wrapped_f
        Command.commandcapability[command.__name__] = self.decorator_kwargs['capability']


# Admin Commands
from . import areaedit
from . import areastats
from . import coding
from . import dig
from . import exitedit
from . import helpedit
from . import playerinfo
from . import promote
from . import raceedit
from . import raceslist
from . import reload
from . import roomedit
from . import shutdown
from . import test_command
from . import viewolcdetails

# Player Commands
from . import afk
from . import alias
from . import arealist
from . import beep
from . import close
from . import commandslist
from . import down
from . import east
from . import emote
from . import goto
from . import help
from . import longdescription
from . import look
from . import mmchat
from . import mmtell
from . import move
from . import north
from . import northeast
from . import northwest
from . import ooc
from . import open
from . import prompt
from . import quit
from . import quote
from . import save
from . import say
from . import score
from . import shortdescription
from . import south
from . import southeast
from . import southwest
from . import title
from . import toggle
from . import up
from . import west
from . import who


