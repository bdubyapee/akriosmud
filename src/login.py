#! usr/bin/env python
# Project: Akrios
# Filename: login.py
# 
# File Description: Login system.
# 
# By: Jubelo

import bcrypt
import logging
import os
import time
import json
import uuid

import area
import comm
import event
import grapevine
import helpsys
import races
from math_utils import dice, fuzz
import world
import player
import livingthing


log = logging.getLogger(__name__)

badwords = []

with open(f"{world.dataDir}/badwords.txt") as thefile:
    for eachword in thefile.readlines():
        badwords.append(eachword.strip())


class Login(object):
    def __init__(self, name=''):
        super().__init__()
        self.interp = self.get_char_name
        self.lasthost = ""
        self.lasttime = ""
        self.name = name
        self.newchar = {}
        self.newstats = {}
        self.password = ""
        self.sock = None

    def clear(self):
        self.interp = self.get_char_name
        self.newchar = {}
        self.newstats = {}
        self.sock = None

    def greeting(self):
        self.sock.dispatch(helpsys.get_help('greet', server=True))
        self.sock.dispatch('\n\rPlease choose a character name: ', trail=False)
                
    def get_char_name(self, inp):
        inp = inp.lower()
        if len(inp) < 3 or len(inp) > 15:
            self.sock.dispatch('Character names must be between 3 and 15 characters long.')
            self.sock.dispatch('Enter a character name: ', trail=False)
        elif len(inp.split()) > 1:
            self.sock.dispatch('Character names must only contain one word.')
            self.sock.dispatch('Enter a character name: ', trail=False)
        elif not inp.isalpha():
            self.sock.dispatch('Character names may only contain letters.')
            self.sock.dispatch('Enter a character name: ', trail=False)
        elif inp in badwords or inp in ['admanthos', 'aludra', 'caerdik', 'malyki', 
                                        'myst', 'nephium', 'selucia', 'sirian', 'tharian']:
            self.sock.dispatch('Character name unacceptable.')
            self.sock.dispatch('Enter a character name: ', trail=False)
        else:
            self.name = inp
            if os.path.exists(f"{world.playerDir}/{self.name}.json"):
                with open(f"{world.playerDir}/{self.name}.json") as playerfile:
                    maybeplayer = json.load(playerfile)
                self.password = maybeplayer['password']
                self.lasttime = maybeplayer['lasttime']
                self.lasthost = maybeplayer['lasthost']
                self.sock.dispatch('Please enter your password: ', trail=False)
                self.interp = self.get_char_password
                self.sock.dont_echo_telnet()
            else:
                if world.allownewCharacters:
                    self.sock.dispatch('Is this a new character? ', trail=False)
                    self.interp = self.confirm_new_char
                else:
                    self.sock.dispatch("I'm sorry, we aren't allowing new characters at this time.\n\r")
                    self.sock.dispatch("Contact jubelo@akriosmud.funcity.org for an invite!")
                    self.sock.close()
                                
    def get_char_password(self, inp):
        inp = inp.encode("utf-8")
        if not bcrypt.checkpw(inp, self.password.encode("utf-8")):
            self.sock.dispatch("\n\rI'm sorry, that isn't the correct password. Good bye.")
            self.sock.handle_close()
            self.clear()
            del self
        else:
            self.sock.do_echo_telnet()
            for person in player.playerlist:
                if person.name == self.name:
                    self.sock.dispatch("\n\rYour character seems to be logged in already.  Reconnecting you.")
                    del person.sock.owner
                    person.sock.close()
                    del person.sock
                    testsock = self.sock
                    self.clear()
                    person.sock = testsock
                    person.sock.owner = person
                    person.sock.promptable = True
                    person.write = person.sock.dispatch
                    comm.wiznet(f"{person.name} reconnecting from link death.")
                    return
            comm.wiznet(f"{self.name.capitalize()} logged into main menu.")
            self.sock.dispatch("")
            self.sock.dispatch("")
            self.sock.dispatch(f"Welcome back {self.name.capitalize()}!")
            self.sock.dispatch(f"You last logged in on {self.lasttime}")
            self.sock.dispatch(f"From this host: {self.lasthost}")
            self.sock.dispatch("")
            log.info(f"{self.name.capitalize()} logged into main menu. Last login {self.lasttime} from {self.lasthost}")
            self.lasttime = time.ctime()
            self.lasthost = self.sock.host.strip()
            self.main_menu()
            self.interp = self.main_menu_get_option
                        
    def confirm_new_char(self, inp):
        inp = inp.lower()
        if inp == "y" or inp == "yes":
            self.sock.dont_echo_telnet()
            self.sock.dispatch("Please choose a password for this character: ", trail=False)
            self.interp = self.confirm_new_password
        else:
            self.sock.dispatch("Calm down.  Take a deep breath.  Now, lets try this again shall we?")
            self.sock.dispatch("Enter a character name: ", trail=False)
            self.interp = self.get_char_name
                        
    def confirm_new_password(self, inp):
        self.sock.dispatch("")
        if len(inp) < 8 or len(inp) > 30:
            self.sock.dispatch("Passwords must be between 8 and 30 characters long.")
            self.sock.dispatch("Please choose a password for this character: ", trail=False)
        else:
            self.password = inp
            self.sock.dispatch("Please reenter your password to confirm: ", trail=False)
            self.interp = self.confirm_new_password_reenter
                        
    def confirm_new_password_reenter(self, inp):
        if inp != self.password:
            self.password = ''
            self.sock.dispatch('')
            self.sock.dispatch('Passwords do not match.')
            self.sock.dispatch('Please choose a password for this character: ', trail=False)
            self.interp = self.confirm_new_password
        else:
            inp = inp.encode('utf-8')
            self.password = bcrypt.hashpw(inp[:71], bcrypt.gensalt(10)).decode('utf-8')
            self.sock.do_echo_telnet()
            self.show_races()
            self.sock.dispatch('Please choose a race: ', trail=False)
            self.interp = self.get_race
                        
    def main_menu(self):
        self.sock.dispatch('{BWelcome to Akrios{x')
        self.sock.dispatch('-=-=-=====-=-=-')
        self.sock.dispatch('1) Login your character')
        self.sock.dispatch('2) View the Message of the Day')
        self.sock.dispatch('L) Logout')
        self.sock.dispatch('D) Delete this character')
        self.sock.dispatch('')
        self.sock.dispatch('Please choose an option: ', trail=False)
                
    def main_menu_get_option(self, inp):
        inp = inp.lower()
        if inp == '1':
            self.interp = self.character_login
            self.interp()
        elif inp == '2':
            self.sock.dispatch(helpsys.get_help('motd', server=True))
            self.sock.dispatch('')
            self.main_menu()
        elif inp == 'l':
            self.sock.dispatch('Thanks for playing.  We hope to see you again soon.')
            log.info(f"{self.sock.host} disconnecting from Akrios.")
            comm.wiznet(f"{self.sock.host} disconnecting from Akrios.")
            self.sock.handle_close()
            self.clear()
            del self
        elif inp == 'd':
            self.sock.dispatch('Sorry to see you go.  Come again soon!')
            log.info(f"Character {self.name} deleted by {self.sock.host}")
            comm.wiznet(f"Character {self.name} deleted by {self.sock.host}")
            os.remove(f"{world.playerDir}/{self.name}.json")
            self.sock.handle_close()
            self.clear()
            del self
        else:
            self.main_menu()
                        
    def character_login(self):
        path = f"{world.playerDir}/{self.name}.json"
        if os.path.exists(path):
            newobject = player.Player(path)
            testsock = self.sock
            self.clear()
            newobject.sock = testsock
            newobject.sock.owner = newobject
            newobject.sock.promptable = True
            newobject.write = newobject.sock.dispatch
            newobject.write("")
            newobject.write(helpsys.get_help("motd", server=True))
            newobject.write("")
            comm.wiznet(f"{newobject.name.capitalize()} logging into Akrios.")
            player.playerlist.append(newobject)
            player.playerlist_by_name[newobject.name] = newobject
            player.playerlist_by_aid[newobject.aid] = newobject
            event.init_events_player(newobject)
            newobject.logpath = os.path.join(world.logDir, f"{newobject.name}.log")
            log.info(f"{newobject.name.capitalize()} logging in from: {newobject.sock.host}")
            if newobject.position == "sleeping":
                newobject.write("You are sleeping.")
            else:
                newobject.interp("look")
            if grapevine.LIVE:
                log.debug(f"Sending player login to Grapevine : {newobject.name}")
                grapevine.gsocket.msg_gen_player_login(newobject.name)
            newobject.lasttime = time.ctime()
            newobject.lasthost = newobject.sock.host
        else:
            self.sock.dispatch("There seems to be a problem loading your file!  Notify Jubelo.")
            log.error(f"{path} does not exist!")
            self.main_menu()
            self.interp = self.main_menu_get_option
                        
    def show_races(self):
        self.sock.dispatch('')
        self.sock.dispatch('\n\rCurrently available races of Akrios')
        self.sock.dispatch('Please type "{Bhelp <race name>{x" for details')
        self.sock.dispatch('')

        good_races = races.race_names_by_alignment('good')
        neutral_races = races.race_names_by_alignment('neutral')
        evil_races = races.race_names_by_alignment('evil')

        self.sock.dispatch(f"{{BGood races{{x: {good_races.title()}")
        self.sock.dispatch(f"{{BNeutral races{{x: {neutral_races.title()}")
        self.sock.dispatch(f"{{BEvil races{{x: {evil_races.title()}")
        self.sock.dispatch('')
                        
    def get_race(self, inp):
        inp = inp.lower()
        if inp in races.racesdict:
            self.newchar['race'] = races.racebyname(inp)
            self.sock.dispatch('')
            self.sock.dispatch("Available genders are: {BFemale Male{x")
            self.sock.dispatch('Please choose a gender: ', trail=False)
            self.interp = self.get_gender
        elif len(inp.split()) > 1:
            if inp.split()[0] == 'help' and inp.split()[1] in races.racesdict:
                self.sock.dispatch(helpsys.get_help(inp.split()[1], server=True))
                self.show_races()
                self.sock.dispatch('Please choose a race: ', trail=False)
        else:
            self.sock.dispatch('That is not a valid race.')
            self.show_races()
            self.sock.dispatch('Please choose a race: ', trail=False)

    def get_gender(self, inp):
        inp = inp.lower()
        if inp in livingthing.genders:
            self.newchar['gender'] = inp
            self.show_disciplines()
            self.sock.dispatch('Please choose a base discipline: ', trail=False)
            self.interp = self.get_discipline
        else:
            self.sock.dispatch("That isn't a valid gender.")
            self.sock.dispatch("Available genders are: {BFemale Male{x")
            self.sock.dispatch("Please choose a gender: ", trail=False)
        
    def show_disciplines(self):
        self.sock.dispatch('')
        self.sock.dispatch('Current base disciplines of Akrios:')
        self.sock.dispatch('Please type "{Bhelp <discipline>{x" for details.')
        self.sock.dispatch('')
        disciplines = ', '.join(livingthing.disciplines)
        self.sock.dispatch(f"{{B{disciplines.title()}{{x")
        self.sock.dispatch('')
        
    def get_discipline(self, inp):
        inp = inp.lower()
        if inp in livingthing.disciplines:
            self.newchar['discipline'] = inp
            self.roll_stats()
            self.show_stats()
            self.sock.dispatch('Are these statistics acceptable? ', trail=False)
            self.interp = self.get_roll_stats
        elif len(inp.split()) > 1: 
            if inp.split()[0] == 'help' and inp.split()[1] in livingthing.disciplines:
                self.sock.dispatch(helpsys.get_help(inp.split()[1], server=True))
                self.show_disciplines()
                self.sock.dispatch('Please choose a base discipline: ', trail=False)
        else:
            self.sock.dispatch('That is not a valid discipline.  Choose a discipline: ', trail=False)
            self.show_disciplines()
            
    def roll_stats(self):
        bonus = 0
        if dice(1, 20) == 20:
            bonus += 5
        if dice(1, 100) == 100:
            bonus += 10
          
        # Set base stat to the race default
        self.newstats['strength'] = fuzz(-5, 4, self.newchar['race'].strength)
        self.newstats['intelligence'] = fuzz(-5, 4, self.newchar['race'].intelligence)
        self.newstats['wisdom'] = fuzz(-5, 4, self.newchar['race'].wisdom)
        self.newstats['agility'] = fuzz(-5, 4, self.newchar['race'].agility)
        self.newstats['speed'] = fuzz(-5, 4, self.newchar['race'].speed)
        self.newstats['charisma'] = fuzz(-5, 4, self.newchar['race'].charisma)
        self.newstats['luck'] = fuzz(-5, 4, self.newchar['race'].luck)
        self.newstats['constitution'] = fuzz(-5, 4, self.newchar['race'].constitution)
        self.newstats['strength'] += dice(2, 3, bonus)
        self.newstats['intelligence'] += dice(2, 3, bonus)
        self.newstats['wisdom'] += dice(2, 3, bonus)
        self.newstats['agility'] += dice(2, 3, bonus)
        self.newstats['speed'] += dice(2, 3, bonus)
        self.newstats['charisma'] += dice(2, 3, bonus)
        self.newstats['luck'] += dice(2, 3, bonus)
        self.newstats['constitution'] += dice(2, 3, bonus)
        
    def show_stats(self):
        self.sock.dispatch('')
        self.sock.dispatch('Randomly rolled statistics:')
        for item in self.newstats.keys():
            self.sock.dispatch(f"{item.capitalize()} {{B{self.newstats[item]}{{x")
        self.sock.dispatch('')
                        
    def get_roll_stats(self, inp):
        inp = inp.lower()
        if inp == 'y' or inp == 'yes':
            self.sock.dispatch(helpsys.get_help('motd', server=True))
            self.sock.dispatch('')
            newplayer = player.Player()
            newplayer.filename = f"{world.playerDir}/{self.name}.json"
            testsock = self.sock
            newplayer.name = self.name
            newplayer.password = self.password
            newplayer.lasttime = time.ctime()
            newplayer.lasthost = self.sock.host
            newplayer.race = self.newchar['race']
            newplayer.aid = str(uuid.uuid4())
            newplayer.equipped = {k: None for k in newplayer.race.wearlocations}
            newplayer.gender = self.newchar['gender']
            newplayer.discipline = self.newchar['discipline']
            newplayer.position = 'standing'
            newplayer.maximum_stat = self.newstats
            newplayer.current_stat = self.newstats
            self.clear()
            newplayer.sock = testsock
            newplayer.sock.owner = newplayer
            newplayer.prompt = '{pAkriosMUD{g:{x '
            newplayer.sock.promptable = True
            newplayer.write = newplayer.sock.dispatch
            player.playerlist.append(newplayer)
            player.playerlist_by_name[newplayer.name] = newplayer
            player.playerlist_by_aid[newplayer.aid] = newplayer
            newroom = area.room_by_vnum_global(1001)
            newplayer.move(newroom)
            newplayer.alias['s'] = 'south'
            newplayer.alias['n'] = 'north'
            newplayer.alias['e'] = 'east'
            newplayer.alias['w'] = 'west'
            newplayer.alias['ne'] = 'northeast'
            newplayer.alias['nw'] = 'northwest'
            newplayer.alias['sw'] = 'southwest'
            newplayer.alias['se'] = 'southeast'
            newplayer.alias['l'] = 'look'
            newplayer.alias['page'] = 'beep'
            newplayer.alias['u'] = 'up'
            newplayer.alias['d'] = 'down'
            newplayer.interp('look')
            newplayer.save()
            event.init_events_player(newplayer)
            log.info(f"{newplayer.name} @ {newplayer.sock.host} is a new character entering Akrios.")
            comm.wiznet(f"{newplayer.name} is a new character entering Akrios.")
            del self
        else:
            self.roll_stats()
            self.show_stats()
            self.sock.dispatch('Are these statistics acceptable? ', trail=False)
