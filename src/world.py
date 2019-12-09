#! usr/bin/env python
# Project: Akrios
# Filename: world.py
# 
# File Description: Contains Pythonic Constants for file locations
#
# By: Jubelo

import os
local = True

# Directory Configuration values
if local:
    homeDir = "/home/bwp/PycharmProjects/akriosmud/"
else:
    homeDir = "/home/bwp/programming/muds/akrios/"
dataDir = os.path.join(homeDir, "data")
logDir = os.path.join(dataDir, "log")
helpDir = os.path.join(dataDir, "help")
playerDir = os.path.join(dataDir, "players")
raceDir = os.path.join(dataDir, "races")
areaDir = os.path.join(dataDir, "areas")

serverlog = os.path.join(logDir, "server.log")


# Generic Configurable Variables
allownewCharacters = True
