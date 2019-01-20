#! usr/bin/env python3
# Project: Akriso
# Filename: commands/score.py
#
# Capability: player
# 
# Command Description: This command displays the score informational screen to the player.
#
# By: Jubelo

from commands import *

name = "score"
version = 1

requirements = {'capability': 'player',
                'generic_fail': "See {WHelp score{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}

@Command(**requirements)
def score(caller, args):
    caller.write("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=Player Information=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    caller.write("Name: {0} {1}".format(caller.name.capitalize(), caller.title))
    caller.write("Gender: {0}  Race: {1} Discipline: {2}".format(caller.gender.capitalize(), caller.race.name.capitalize(), caller.discipline.capitalize()))
    caller.write("Short Desc: {0}".format(caller.short_description))
    caller.write("Capabilities: {0}".format(', '.join(caller.capability)))
    caller.write(f"Position: {caller.position.capitalize()}")
    caller.write("Alignment: {0}  Age: {1} Weight: {2} Height: {3}'{4}".format(caller.alignment, caller.age, caller.weight, caller.height['feet'], caller.height['inches']))
    caller.write("")
    caller.write("Platinum: {0} Gold: {1} Silver: {2} Copper: {3}".format(caller.money['platinum'], caller.money['gold'], caller.money['silver'], caller.money['copper']))
    caller.write("")
    caller.write("HP: {0}/{1} Hitroll: {2}".format(caller.currenthp, caller.maxhp, caller.hitroll))
    caller.write("Movement: {0}/{1} Damroll: {2}".format(caller.currentmovement, caller.maxmovement, caller.damroll))
    caller.write("Will Power: {0}/{1} Wimpy: {2}".format(caller.currentwillpower, caller.maxwillpower, caller.wimpy))
    caller.write("")
    caller.write("Family: {0} Clan: {1} Guild: {2} Council: {3}".format(caller.family, caller.clan, caller.guild, caller.council))
    caller.write("")
    caller.write("You are worshipping: {0}".format(caller.deity))
    caller.write("You have {0} skill points to spend.".format(caller.skillpoints))
    caller.write("")
    caller.write("AC Slashing: {0:>2}/{1:<2}         Strength: {2:>2}/{3:<2}          Agility: {4:>2}/{5:<2}".format(caller.currentac['slashing'], caller.baceac['slashing'], caller.current_stat['strength'], caller.maximum_stat['strength'], caller.current_stat['agility'], caller.maximum_stat['agility']))
    caller.write(" AC Bashing: {0:>2}/{1:<2}     Intelligence: {2:>2}/{3:<2}            Speed: {4:>2}/{5:<2}".format(caller.currentac['bashing'], caller.baceac['bashing'], caller.current_stat['intelligence'], caller.maximum_stat['intelligence'], caller.current_stat['speed'], caller.maximum_stat['speed']))
    caller.write("AC Piercing: {0:>2}/{1:<2}           Wisdom: {2:>2}/{3:<2}     Constitution: {4:>2}/{5:<2}".format(caller.currentac['piercing'], caller.baceac['piercing'], caller.current_stat['wisdom'], caller.maximum_stat['wisdom'], caller.current_stat['constitution'], caller.maximum_stat['constitution']))
    caller.write(" AC Lashing: {0:>2}/{1:<2}             Luck: {2:>2}/{3:<2}         Charisma: {4:>2}/{5:<2}".format(caller.currentac['lashing'], caller.baceac['lashing'], caller.current_stat['luck'], caller.maximum_stat['luck'], caller.current_stat['charisma'], caller.maximum_stat['charisma']))
    caller.write("")
    caller.write("Location: {0}".format(caller.location.vnum))


