# Project: Akrios
# Filename: commands/areaedit.py
#
# Capability: builder
#
# Command Description: Entry into area editing mode for builders and admins.
#
# By: Jubelo

from commands import *

name = "areaedit"
version = 1

@Command(capability="admin")
def areaedit(caller, args):
    helpstring = "Please see {Whelp areaedit{x for instructions."
    args = args.split()
    isBuilding = hasattr(caller, 'building')
    isEditing = hasattr(caller, 'editing')

    if len(args) == 0:
        if isBuilding:
            caller.write(caller.building.display())
            return

    if isBuilding:
        if args[0] == 'done':
            caller.building.save()
            caller.building.builder = None
            del(caller.building)
            caller.prompt = caller.oldprompt
            del(caller.oldprompt)
        elif args[0] == 'new':
            caller.write("You are already editing an area.")
            return
        elif args[0] == 'populate':
            myarea = caller.building
            myvnum = caller.building.vnumlow
            if myvnum in area.roomlist.keys():
                caller.write("That room already exists.  Please edit it directly.")
                return
            else:
                newroom = room.oneRoom(caller.building, vnum=myvnum)
                area.roomlist[myvnum] = newroom
                newroom.area.roomlist[myvnum] = newroom
                caller.write(f"First new room {newroom.vnum} has been created.")
        elif args[0] in caller.building.commands:
            caller.building.doAttrib(args[0], ' '.join(args[1:]))
        else:
            caller.write(helpstring)
    else:
        if args[0] == 'new':
            mynewname = args[1:]
            path = os.path.join(world.areaDir, ' '.join(args[1:]))
            newarea = area.oneArea(path)
            caller.building = newarea
            area.arealist.append(newarea)
            caller.building.builder = caller
            caller.write(f"Editing {{W{args[1:]}{{x")
            caller.oldprompt = caller.prompt
            caller.prompt = "areaEdit:> "
        elif args[0] == 'save':
            caller.location.area.save()
            caller.write("Area has been saved.")
        elif args[0] == 'here':
            caller.building = caller.location.area
            caller.building.builder = caller
            caller.write(f"Editing area: {{W{caller.location.area.name}{{x.")
            caller.write(helpstring)
            caller.oldprompt = caller.prompt
            caller.prompt = "areaEdit:> "
            caller.write(caller.building.display())
        else:
            caller.write(helpstring)


