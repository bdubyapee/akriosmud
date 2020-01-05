#! usr/bin/env python
# Project: Akrios
# Filename: event.py
# 
# File Description: Module to handle event queues.
# 
# By: Jubelo

import logging
import random
import time
import uuid

import area
import comm
import frontend
import grapevine
import player
import server

log = logging.getLogger(__name__)

PULSE_PER_SECOND = 16
PULSE_PER_MINUTE = 60 * PULSE_PER_SECOND


class Queue(object):
    def __init__(self, owner, owner_type):
        super().__init__()
        self.aid = str(uuid.uuid4())
        self.eventlist = []
        self.owner = owner
        self.owner_type = owner_type

    def add(self, event):
        if self.is_empty():
            things_with_events[self.owner_type].append(self.owner)
        self.eventlist.append(event)

    def remove(self, event):
        # Some events may be destroyed within an event.  Player auto quit
        # and a player being forced to drop within an event and having their
        # queue cleared is one example.
        if event in self.eventlist:
            self.eventlist.remove(event)
        if self.is_empty():
            if self.owner in things_with_events[self.owner_type]:
                things_with_events[self.owner_type].remove(self.owner)

    def remove_event_type(self, eventtype=None):
        if eventtype is None:
            return
        for eachevent in self.eventlist:
            if eachevent.eventtype == eventtype:
                self.eventlist.remove(eachevent)

    def update(self):
        for event in self.eventlist:
            if event is None or event.func is None:
                self.eventlist.remove(event)
                return
            event.passes -= 1
            if event.passes <= 0:
                event.fire()
       
    def clear(self):
        for eachthing in things_with_events[self.owner_type]:
            if eachthing == self.owner:
                things_with_events[self.owner_type].remove(eachthing)
        self.eventlist = []

    def num_events(self):
        return len(self.eventlist)

    def is_empty(self):
        if not self.eventlist:
            return True
        else:
            return False


class Event(object):
    def __init__(self):
        super().__init__()
        self.aid = str(uuid.uuid4())
        self.eventtype = None
        self.ownertype = None
        self.owner = None
        self.func = None
        self.arguments = None
        self.passes = 0
        self.totalpasses = 0

    def fire(self):
        self.func(self)
        owner_exists = self.owner is not None
        owner_has_events_attrib = hasattr(self.owner, "events")
        if owner_exists and owner_has_events_attrib:
            self.owner.events.remove(self)
        

things_with_events = {"player": [],
                      "area": [],
                      "room": [],
                      "exit": [],
                      "mobile": [],
                      "object": [],
                      "reset": [],
                      "server": [],
                      "frontend": [],
                      "session": [],
                      "grapevine": []}


def heartbeat():
    for each_event_type in things_with_events:
        for each_queue in things_with_events[each_event_type]:
            each_queue.events.update()


# Below are the init functions.  If a particular thing needs to have
# an event set when it's created, it should go inside the appropriate
# init below.

def init_events_session(session):
    log.debug(f'Initializing events_session: {session}')


def init_events_server(server_):
    log.debug(f"Initializing events_server: {server_}")


def init_events_frontend(frontend_):
    log.debug(f"Initializing events_frontend: {frontend_}")

    event = Event()
    event.owner = frontend_
    event.ownertype = "frontend"
    event.eventtype = "frontend receive"
    event.func = event_frontend_receive_message
    event.passes = 1
    event.totalpasses = event.passes
    frontend_.events.add(event)

    event = Event()
    event.owner = frontend_
    event.ownertype = "frontend"
    event.eventtype = "frontend send"
    event.func = event_frontend_send_message
    event.passes = 1
    event.totalpasses = event.passes
    frontend_.events.add(event)

    event = Event()
    event.owner = frontend_
    event.ownertype = "frontend"
    event.eventtype = "frontend state check"
    event.func = event_frontend_state_check
    event.passes = 3 * PULSE_PER_MINUTE
    event.totalpasses = event.passes
    frontend_.events.add(event)


def init_events_grapevine(grapevine_):
    log.debug("Initializing events_grapevine")
    event = Event()
    event.owner = grapevine_
    event.ownertype = "grapevine"
    event.eventtype = "grapevine receive"
    event.func = event_grapevine_receive_message
    event.passes = 1 * PULSE_PER_SECOND
    event.totalpasses = event.passes
    grapevine_.events.add(event)

    event = Event()
    event.owner = grapevine_
    event.ownertype = "grapevine"
    event.eventtype = "grapevine send"
    event.func = event_grapevine_send_message
    event.passes = 1 * PULSE_PER_SECOND
    event.totalpasses = event.passes
    grapevine_.events.add(event)

    event = Event()
    event.owner = grapevine_
    event.ownertype = "grapevine"
    event.eventtype = "grapevine state check"
    event.func = event_grapevine_state_check
    event.passes = 3 * PULSE_PER_MINUTE
    event.totalpasses = event.passes
    grapevine_.events.add(event)


def init_events_area(area_):
    log.debug(f"Initializing events_area: {area_}")


def init_events_room(room):
    log.debug(f"Initializing events_room: {room}")


def init_events_reset(reset):
    log.debug(f"Initializing events_reset: {reset}")


def init_events_exit(exit_):
    log.debug(f"Initializing events_exit: {exit_}")


def init_events_mobile(mobile):
    log.debug(f"Initializing events_mobile: {mobile}")


def init_events_player(player_):
    log.debug(f"Initializing events_player: {player_}")
    # Begin with events _all_ players will have.

    # First is the autosave for players every 5 minutes
    event = Event()
    event.owner = player_
    event.ownertype = "player"
    event.eventtype = "autosave"
    event.func = event_player_autosave
    event.passes = 5 * PULSE_PER_MINUTE
    event.totalpasses = event.passes
    player_.events.add(event)

    # Check for player idle time here once per minute.
    event = Event()
    event.owner = player_
    event.ownertype = "player"
    event.eventtype = "idle check"
    event.func = event_player_idle_check
    event.passes = 1 * PULSE_PER_MINUTE
    event.totalpasses = event.passes
    player_.events.add(event)

    # Player dependant events go below here.

    # If player is a newbie, or has the flag enabled send them newbie tips.
    if player_.oocflags_stored['newbie'] == 'true':
        event = Event()
        event.owner = player_
        event.ownertype = "player"
        event.eventtype = "newbie tips"
        event.func = event_player_newbie_notify
        event.passes = 45 * PULSE_PER_SECOND
        event.totalpasses = event.passes
        player_.events.add(event)
        if player_.sock is None:
            return
        player_.sock.dispatch("\n\r{P[NEWBIE TIP]{x: You will receive Newbie Tips periodically "
                              "until disabled.\n\r              Use the 'toggle newbie' command "
                              "to enable/disable")

    # Admin characters will receive a system status update.
    if player_.is_admin:
        event = Event()
        event.owner = player_
        event.ownertype = "admin"
        event.eventtype = "system status"
        event.func = event_admin_system_status
        event.passes = 5 * PULSE_PER_MINUTE
        event.totalpasses = event.passes
        player_.events.add(event)


def init_events_object(object_):
    log.debug(f"Initializing events_object: {object_}")


# Below are the actual events.
# Some events will be reoccuring.  Those events can be decorated with the
# reoccuring_event decorator to automate the creation of the next event.

def reoccuring_event(func_to_decorate):
    def new_func(*args, **kwargs):
        event, = args
        nextevent = Event()
        nextevent.owner = event.owner
        nextevent.ownertype = event.ownertype
        nextevent.eventtype = event.eventtype
        nextevent.func = event.func
        nextevent.passes = event.totalpasses
        nextevent.totalpasses = event.totalpasses
        event.owner.events.add(nextevent)

        return func_to_decorate(*args, **kwargs)

    return new_func


def event_frontend_restart(fe_):
    comm.wiznet("Front end restart event initiated")
    del frontend.fesocket

    frontend.fesocket = frontend.FESocket()
    frontend_connected = frontend.fesocket.fesocket_connect()
    if not frontend_connected:
        comm.wiznet("Could not connect to Front End in event restart")


@reoccuring_event
def event_frontend_send_message(event_):
    if event_.owner.outbound_frame_buffer:
        event_.owner.handle_write()


@reoccuring_event
def event_frontend_heartbeat(event_):
    fe_ = event_.owner
    fe_.msg_gen_heartbeat()


@reoccuring_event
def event_frontend_receive_message(event_):
    fe_ = event_.owner
    fe_.handle_read()
    if fe_.inbound_frame_buffer:
        # Assign rcvd_msg to a FEReceivedMessage instance.
        rcvd_msg = fe_.receive_message()
        ret_value = rcvd_msg.parse_frame()

        log.info(f'Received : {rcvd_msg.message}')

        if ret_value:
            if rcvd_msg.message['event'] == "player/input":
                uuid_, addr, port, message = ret_value
                if uuid_ in server.session_list:
                    log.info(f'uuid_ in server.session_list')
                    log.info(f'session_list: {server.session_list}')
                    server.session_list[uuid_].inbuf.append(message)
                    log.info(f'Appended to inbuf: {server.session_list[uuid_].inbuf}')
                return

            if rcvd_msg.message['event'] == 'connection/connected':
                uuid_, addr_, port_ = ret_value
                log.info(f'Creating connected session: {uuid_}')
                server.Session(uuid_, addr_, port_)
                log.info(f'SESSION LIST: {server.session_list}')

            if rcvd_msg.message['event'] == 'connection/disconnected':
                uuid_, addr_, port_ = ret_value
                if uuid_ not in server.session_list:
                    log.warning('Trying to disconnect session not in session_list:')
                    log.warning(f'{uuid_} not in {server.session_list.keys()}')
                else:
                    log.info(f'Disconnecting session {uuid_}')
                    player_ = server.session_list[uuid_]
                    if player_.state['logged in']:
                        player_.interp('save')
                        player_.interp('quit force')
                        pass
                    server.session_list.pop(uuid_)
                    player_.clear()

            if 'event' in rcvd_msg.message and rcvd_msg.message['event'] == 'restart':
                comm.wiznet("Received restart event from Front End.")
                restart_fuzz = 15 + rcvd_msg.restart_downtime

                fe_.fesocket_disconnect()

                nextevent = Event()
                nextevent.owner = fe_
                nextevent.ownertype = "frontend"
                nextevent.eventtype = "frontend restart"
                nextevent.func = event_frontend_restart
                nextevent.passes = restart_fuzz * PULSE_PER_SECOND
                nextevent.totalpasses = nextevent.passes
                fe_.events.add(nextevent)


@reoccuring_event
def event_frontend_state_check(event_):
    fe_ = event_.owner

    if time.time() - fe_.last_heartbeat > 60:
        log.info('Setting front end state to disconnected due to > 60 seconds with no heartbeat.')
        fe_.state["connected"] = False

    if fe_.state["connected"]:
        return
    else:
        for each_thing in things_with_events['frontend']:
            for each_event in each_thing.events.eventlist:
                if each_event.eventtype == "frontend restart":
                    return

        fe_.fesocket_disconnect()

        nextevent = Event()
        nextevent.owner = fe_
        nextevent.ownertype = "frontend"
        nextevent.eventtype = "frontend restart"
        nextevent.func = event_frontend_restart
        nextevent.passes = 30 * PULSE_PER_SECOND
        nextevent.totalpasses = nextevent.passes
        fe_.events.add(nextevent)


def event_grapevine_restart():
    comm.wiznet("Grapevine restart event initiated")
    del grapevine.gsocket

    grapevine.gsocket = grapevine.GrapevineSocket()
    grapevine_connected = grapevine.gsocket.gsocket_connect()
    if not grapevine_connected:
        comm.wiznet("Could not connect to Grapevine in event restart")


@reoccuring_event
def event_grapevine_send_message(event_):
    if event_.owner.outbound_frame_buffer:
        event_.owner.handle_write()


@reoccuring_event
def event_grapevine_receive_message(event_):
    grapevine_ = event_.owner
    grapevine_.handle_read()
    if grapevine_.inbound_frame_buffer:
        # Assign rcvd_msg to a GrapevineReceivedMessage instance.
        rcvd_msg = grapevine_.receive_message()
        ret_value = rcvd_msg.parse_frame()

        if ret_value:
            # We will receive a "tells/send" if there was an error telling a
            # foreign game player.
            if rcvd_msg.message['event'] == "tells/send":
                caller, target, game, error_msg = ret_value
                message = (f"\n\r{{GGrapevine Tell to {{y{target}@{game}{{G "
                           f"returned an Error{{x: {{R{error_msg}{{x")
                for eachplayer in player.playerlist:
                    if eachplayer.disp_name == caller:
                        if eachplayer.oocflags_stored['grapevine'] == 'true':
                            eachplayer.write(message)
                            return

            if rcvd_msg.message['event'] == "tells/receive":
                sender, target, game, sent, message = ret_value
                message = (f"\n\r{{GGrapevine Tell from {{y{sender}@{game}{{x: "
                           f"{{G{message}{{x.\n\rReceived at : {sent}.")
                for eachplayer in player.playerlist:
                    if eachplayer.disp_name == target.capitalize():
                        if eachplayer.oocflags_stored['grapevine'] == 'true':
                            eachplayer.write(message)
                            return

            if rcvd_msg.message['event'] == "games/status":
                if ret_value:
                    # We've received a game status request response from
                    # grapevine.  Do what you will here with the information,
                    # Not going to do anything with it in Akrios at the moment.
                    return

            # Received Grapevine Info that goes to all players goes here.
            message = ""
            channel = ""
            is_status_msg = False

            if rcvd_msg.message['event'] == "games/connect":
                game = ret_value.capitalize()
                message = f"\n\r{{GGrapevine Status Update: {game} connected to network{{x"
                is_status_msg = True
            if rcvd_msg.message['event'] == "games/disconnect":
                game = ret_value.capitalize()
                message = f"\n\r{{GGrapevine Status Update: {game} disconnected from network{{x"
                is_status_msg = True
            if rcvd_msg.message['event'] == "channels/broadcast":
                name, game, message, channel = ret_value
                if name is None or game is None:
                    comm.wiznet("Received channels/broadcast with None type")
                    return
                message = (f"\n\r{{GGrapevine {{B{channel}{{x Chat{{x:{{y{name.capitalize()}"
                           f"@{game.capitalize()}{{x:{{G{message}{{x")
            if rcvd_msg.is_other_game_player_update():
                name, inout, game = ret_value
                if name is None or game is None:
                    comm.wiznet("Received other game player update")
                    return
                message = (f"\n\r{{GGrapevine Status Update{{x: {{y{name.capitalize()}{{G "
                           f"has {inout} {{Y{game.capitalize()}{{x.")
                is_status_msg = True

            if message != "":
                grape_enabled = [players for players in player.playerlist
                                 if players.oocflags_stored['grapevine'] == 'true']
                if is_status_msg:
                    for eachplayer in grape_enabled:
                        eachplayer.write(message)
                else:
                    for eachplayer in grape_enabled:
                        if channel in eachplayer.oocflags['grapevine_channels']:
                            eachplayer.write(message)
                return

        if 'event' in rcvd_msg.message and rcvd_msg.message['event'] == 'restart':
            comm.wiznet("Received restart event from Grapevine.")
            restart_fuzz = 15 + rcvd_msg.restart_downtime
 
            grapevine_.gsocket_disconnect()

            nextevent = Event()
            nextevent.owner = grapevine_
            nextevent.ownertype = "grapevine"
            nextevent.eventtype = "grapevine restart"
            nextevent.func = event_grapevine_restart
            nextevent.passes = restart_fuzz * PULSE_PER_SECOND
            nextevent.totalpasses = nextevent.passes
            grapevine_.events.add(nextevent)


@reoccuring_event
def event_grapevine_state_check(event_):
    grapevine_ = event_.owner

    if time.time() - grapevine_.last_heartbeat > 60:
        grapevine_.state["connected"] = False
        grapevine_.state["authenticated"] = False

    if grapevine_.state["connected"]:
        grapevine_.other_games_players = {}
        grapevine_.msg_gen_player_status_query()
        return
    else:
        for each_thing in things_with_events['grapevine']:
            for each_event in each_thing.events.eventlist:
                if each_event.eventtype == "grapevine restart":
                    return

        grapevine_.gsocket_disconnect()

        nextevent = Event()
        nextevent.owner = grapevine_
        nextevent.ownertype = "grapevine"
        nextevent.eventtype = "grapevine restart"
        nextevent.func = event_grapevine_restart
        nextevent.passes = 30 * PULSE_PER_SECOND
        nextevent.totalpasses = nextevent.passes
        grapevine_.events.add(nextevent)


@reoccuring_event
def event_admin_system_status(event_):
    if event_.owner.is_building or event_.owner.is_editing:
        return

    event_count = {'player': 0,
                   'mobile': 0,
                   'object': 0,
                   'area': 0,
                   'room': 0,
                   'reset': 0,
                   'exit': 0,
                   'server': 0,
                   'session': 0,
                   'frontend': 0,
                   'grapevine': 0}

    for each_type in things_with_events:
        for each_thing in things_with_events[each_type]:
            event_count[each_type] += each_thing.events.num_events()

    moblist_index = 0
    moblist = 0
    objlist_index = 0
    objlist = 0

    for eacharea in area.arealist:
        moblist_index += len(eacharea.mobilelist_index)
        moblist += len(eacharea.mobilelist)
        objlist_index += len(eacharea.objectlist_index)
        objlist += len(eacharea.objectlist)

    if grapevine.LIVE:
        grapevine_status = grapevine.gsocket.state['connected']
    else:
        grapevine_status = 'Disabled'

    msg = (f"\n\r{{RAkrios System Status (5 minute update){{x\n\r"
           f"{{GPlayer Connections{{x: {{R{len(server.session_list)}{{x\n\r"
           f"{{G      Mobile Index{{x: {{R{moblist_index}{{x\n\r"
           f"{{G           Mobiles{{x: {{R{moblist}{{x\n\r"
           f"{{G      Object Index{{x: {{R{objlist_index}{{x\n\r"
           f"{{G           Objects{{x: {{R{objlist}{{x\n\r"
           f"{{G  Game Events List{{x\n\r"
           f"{{G        Player Events{{x: {{R{event_count['player']}{{x\n\r"
           f"{{G        Mobile Events{{x: {{R{event_count['mobile']}{{x\n\r"
           f"{{G        Object Events{{x: {{R{event_count['object']}{{x\n\r"
           f"{{G          Area Events{{x: {{R{event_count['area']}{{x\n\r"
           f"{{G          Room Events{{x: {{R{event_count['room']}{{x\n\r"
           f"{{G         Reset Events{{x: {{R{event_count['reset']}{{x\n\r"
           f"{{G          Exit Events{{x: {{R{event_count['exit']}{{x\n\r"
           f"{{G        Server Events{{x: {{R{event_count['server']}{{x\n\r"
           f"{{G       Session Events{{x: {{R{event_count['session']}{{x\n\r"
           f"{{G     Front End Events{{x: {{R{event_count['frontend']}{{x\n\r"
           f"{{G     Grapevine Events{{x: {{R{event_count['grapevine']}{{x\n\r"
           f"{{G  Grapevine Connected{{x: {{R{grapevine_status}{{x\n\r")

    event_.owner.write(msg)


@reoccuring_event
def event_player_autosave(event_):
    event_.owner.save()


@reoccuring_event
def event_player_idle_check(event_):
    idle_time = time.time() - event_.owner.last_input
 
    if event_.owner.is_building or event_.owner.is_editing or event_.owner.is_admin:
        return

    if idle_time >= 10 * 60:
        log.info(f"AFK forced log out {event_.owner.name.capitalize()}")
        event_.owner.write("\n\r{WYou have been idle for over 10 minutes.  Logging you out.{x")
        event_.owner.interp('quit force')
        return

    if idle_time > 8 * 60:
        event_.owner.write("\n\r{WYou have been idle for over 8 minutes. Auto logout in 2 minutes.{x")
        event_.owner.sock.send(b'\x07')
        return

    if idle_time >= 5 * 60:
        event_.owner.save()
        if event_.owner.oocflags['afk']:
            return
        event_.owner.write("\n\r{WYou have been idle for over 5 minutes.  Placing you in AFK.{x")
        event_.owner.sock.send(b'\x07')
        event_.owner.oocflags['afk'] = True


@reoccuring_event
def event_player_newbie_notify(event_):
    if event_.owner.oocflags_stored['newbie'] == 'false':
        return

    tips = ["You will receive Newbie Tips periodically until disabled.\n\r"
            "              Use the 'toggle newbie' command to enable/disable.",
            "Type 'help' to see help topics.",
            "You can configure alias' for commands.  See 'help alias' for usage details",
            "Type 'who' to see who else is playing in Akrios.",
            "Type 'commands' to see the commands available to you.",
            "Type 'ooc <message>' to post an Out of Character message to all players in Akrios.",
            "Type 'beep Jubelo' to send a beep to Jubelo if you need help!",
            "Type 'say <message>' to say something to other players in the same room.",
            "Type 'look' to look at the room you are in",
            "Akrios is connected to grapevine.haus for Grapevine Chat!\n\rType"
            " 'toggle grapevine' to disable or 'gchat <message>' to speak to other players!"]
        
    event_.owner.write(f"\n\r{{P[NEWBIE TIP]{{x: {random.choice(tips)}")
