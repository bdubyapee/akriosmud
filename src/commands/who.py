#! usr/bin/env python3
# Project: Akrios
# Filename: commands/who.py
#
# Capability : player
# 
# Command Description: Displays a list of other players, builders and
#                      administrators.
#
# By: Jubelo

from commands import *

name = "who"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp who{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
def who(caller, args, **kwargs):
    
    caller.write("       {W,         {W/|\\")
    caller.write("       {W|\        {W|{PO{W|{D________________________________________________")
    caller.write("       {W|{Yo{W\\{y_______{W|@|{B*                                              {B*{D\\")
    caller.write("        {W>{Po{g\\ \\ \\ \\{W|{YO{W|{B*{D---{RI{D-{RN{D-{RH{D-{RA{D-{RB{D-{RI{D-{RT{D-{RA{D-{RN{D-{RT{D-{RS{D---{RO{D-{RF{D---{RA{D-{RK{D-{RR{D-{RI{D-{RO{D-{RS{D--{B*{D->")
    caller.write("       {W|{Yo{W/{y-{gv{y-{gv{y-{gv{y-{W|@|{B*{D______________________________________________{B*{D/")
    caller.write("       {W|/        {W|{PO{W| ")
    caller.write("       {W'         \\|/{x")
    caller.write("")
    for person in player.playerlist:
        if person.is_admin:
            extra0 = 'ADM'
        elif person.is_deity:
            extra0 = 'DEI'
        elif person.is_builder:
            extra0 = 'BLD'
        else:
            extra0 = person.race.name.capitalize()
        if person.is_building:
            extra1 = '{W[{RBuilding{W]{x'
        elif person.is_editing:
            extra1 = '{W[{REditing{W]{x'
        else:
            extra1 = ''
        if person.oocflags['afk'] is True:
            extra2 = '{W[{RAFK{W]{x'
        elif person.oocflags['coding'] is True:
            extra2 = '{W[{RCoding{W]{x'
        else:
            extra2 = ''
        caller.write("{{W[{{R{0:7} {{B{1:>6}{{W]{{x {2} {3}{4}{5}".format(extra0, person.gender.capitalize(),
                                                                          person.disp_name, person.title, extra2,
                                                                          extra1))

    caller.write("\n\r")

    if not grapevine.LIVE:
        caller.write("{BGrapevine network disabled.{x:")
        return

    caller.write("{BPlayers in other Realms on the Grapevine network{x:")
    caller.write("{Wwho <gamename>{x to see players on other games.")

    if len(args) <= 0 and grapevine.gsocket.other_games_players:
        game_data = [f"{{R{k}{{x: {{W{len(v) or 0}{{x" for k, v in grapevine.gsocket.other_games_players.items()]
        game_data.sort()
        numcols = 5
        while (len(game_data) % numcols) > 0:
            game_data.append(' ')
        for i in range(0, len(game_data), numcols):
            output = ''
            for l in range(0, numcols):
                output = f"{output}{game_data[i + l]:20}"
            caller.write(output)

    if len(args) > 0:
        if args.lower() in grapevine.gsocket.other_games_players:
            if len(grapevine.gsocket.other_games_players[args]) >= 1:
                caller.write("Players connected to {args.capitalize()}:")
                for eachplayer in grapevine.gsocket.other_games_players[args]:
                    caller.write(f"     {eachplayer} {{R@{{x {args.capitalize()}")
        else:
            caller.write(f"{args.capitalize()} is not connected to Grapevine.")
            return
