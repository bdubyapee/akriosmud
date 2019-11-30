#! usr/bin/env python
# Project: Akrios
# Filename: comm.py
# 
# File Description: Communications Module.  Handles low level channel/log stuff.
# 
# By: Jubelo

import logging

import player

log = logging.getLogger(__name__)


def wiznet(msg=""):
    msg = f"\n\r\n\r{{YWiznet: {msg.capitalize()[0]}{msg[1:]}{{x"
    log.info(msg.lstrip())
    for person in player.playerlist:
        if person.is_admin:
            person.write(msg)


def act():
    pass


def message_to_player(each_player, sender, message=""):
    if not message:
        return

    each_player.write(message)


def message_to_room(room, sender, message=""):
    if not message:
        return

    for eachthing in room.contents:
        if eachthing is not sender and eachthing.is_player:
            eachthing.write(f"\n\r\n\r{message}")


def message_to_area(area, sender, message=""):
    if not message:
        return

    for each_player in area.playerlist:
        each_player.write(message)
