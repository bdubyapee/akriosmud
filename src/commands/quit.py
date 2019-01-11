#! usr/bin/env python3
# Project: Akrios
# filename: commands/quit.py
#
# Capability : player
#
# Command Description: The quit command for players.
#
# By: Jubelo

from commands import *

name = 'quit'
version = 1


@Command(capability='player')
def quit(caller, args, **kwargs):
    isBuilding = hasattr(caller, 'building')
    isEditing = hasattr(caller, 'editing')

    if isBuilding or isEditing:
        caller.write("You must finish building first!")
        return

    caller.save()
    # Notify Gossip of return player logout.
    gossip.gsocket.msg_gen_player_logout(caller.name)
    caller.location.contents.remove(caller)
    caller.sock.promptable = False
    caller.events.clear()
    conn = login.Login(caller.name)
    testsock = caller.sock
    player.playerlist.remove(caller)
    if args == "force":
        reason = "[IDLE TIMEOUT] "
    else:
        reason = ""
    comm.wiznet(f"{reason}{caller.name} logging out of Akrios.")
    del(caller)
    conn.sock = testsock
    conn.sock.owner = conn
    conn.main_menu()
    # Linkdeath/timout will force a quit.  Test for that below so we remove
    # them completely from the game and don't leave them stuck at the menu.
    if args == "force":
        conn.main_menu_get_option('l')
    else:
        conn.interp = conn.main_menu_get_option


