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

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp quit{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def quit(caller, args, **kwargs):
    if caller.is_building or caller.is_editing: 
        caller.write("You must finish building first!")
        return

    caller.save()
    grapevine.gsocket.msg_gen_player_logout(caller.name)
    caller.location.contents.remove(caller)
    caller.sock.promptable = False
    caller.events.clear()
    conn = login.Login(caller.name)
    testsock = caller.sock

    if caller in player.playerlist:
        player.playerlist.remove(caller)
    if caller.name in player.playerlist_by_name:
        player.playerlist_by_name.pop(caller.name)
    if caller.aid in player.playerlist_by_aid:
        player.playerlist_by_aid.pop(caller.aid)
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


