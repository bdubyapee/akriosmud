#! usr/bin/env python
# Project: Akrios
# Filename: atomic.py
# 
# File Description: The atomic module.  House anything that will pertain to all
#                   players, mobiles and objects.
# 
# By: Jubelo

# Imports here
import time

import area
import comm
import commands
import exits
import room


class Atomic(object):
    def __init__(self):
        super().__init__()

    def interp(self, inp=None):

        if len(self.snooped_by) > 0:
            for each_person in self.snooped_by:
                each_person.write(f"{self.name} typed: {inp}")

        inp = inp.split()

        if self.is_player:
            self.oocflags['afk'] = False

        isBuilding = hasattr(self, 'building')
        isEditing = hasattr(self, 'editing')

        self.last_input = time.time()

        if len(inp) == 0:
            if isBuilding and not isEditing:
                self.write(self.building.display())
                return
            if isEditing:
                self.editing.add('')
                return
            else:
                self.write('')
                return

        # Look in living thing command alias dict, swap alias for full command if found        
        if inp[0] in self.alias:
            inp[0] = self.alias[inp[0]]

        comfind = []

        # Added some time ago for OLC to work properly.  Fix this XXX
        if len(inp) <= 0:
            inp = ['']

        for item in sorted(commands.Command.commandhash.keys()):
            if item.startswith(inp[0].lower()):
                comfind.append(commands.Command.commandhash[item])

        if isBuilding:
            types = {helpsys.oneHelp: 'helpedit',
                     races.oneRace: 'raceedit',
                     area.oneArea: 'areaedit',
                     room.oneRoom: 'roomedit',
                     exits.Exit: 'exitedit'}
            if self.building.__class__ in types:
                comfind.append(commands.Command.commandhash[types[self.building.__class__]])
                # If the person is building we prepend the command they are using.
                inp.insert(0, types[self.building.__class__])
                self.write('')

        if len(comfind) > 0:
            try:
                if isEditing:
                    comfind[-1](self, ' '.join(inp[1:]))
                elif isBuilding:
                    if comfind[0].__name__ not in types.values():
                        comfind[0](self, ' '.join(inp[2:]))
                    else:
                        comfind[0](self, ' '.join(inp[1:]))
                else:
                    comfind[0](self, ' '.join(inp[1:]))
            except (NameError, IndexError) as msg:
                self.write(msg)
        else:
            self.write("Huh?")

    def move(self, tospot=None, fromspot=None, direction=None):
        if tospot == None:
            comm.wiznet("Received None value in move:livingthing.py")
        else:
            mover = self.disp_name

            if direction == None:
                rev_direction = "the ether"
            elif direction != "goto":
                rev_direction = exits.oppositedirection[direction]

            if fromspot != None:
                if direction == "goto":
                    fromspot_message = f"{mover} has vanished into thin air."
                else:
                    fromspot_message = f"{mover} has left to the {direction}."
                comm.message_to_room(fromspot, self, fromspot_message)
                fromspot.contents.remove(self)

            # Once object notification is in, notify left room of departure and
            # room we moved to of arrival.

            tospot.contents.append(self)
            self.location = tospot
            if direction == "goto" or fromspot == None:
                tospot_message = f"{mover} has sprung into existence!"
            else:
                tospot_message = f"{mover} has arrived from the {rev_direction}."
            comm.message_to_room(tospot, self, tospot_message)

    @property
    def is_admin(self):
        if 'admin' in self.capability:
            return True
        else:
            return False

    @property
    def is_deity(self):
        if 'deity' in self.capability:
            return True
        else:
            return False

    @property
    def is_builder(self):
        if 'builder' in self.capability:
            return True
        else:
            return False

    @property
    def is_player(self):
        if 'player' in self.capability:
            return True
        else:
            return False

    @property
    def is_mobile(self):
        if 'mobile' in self.capability:
            return True
        else:
            return False

    @property
    def is_object(self):
        if 'object' in self.capability:
            return True
        else:
            return False

    @property
    def disp_name(self):
        return self.name.capitalize() if self.is_player else self.short_description


