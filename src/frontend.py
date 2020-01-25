#! usr/bin/env python3
# Project: Akrios
# Filename: frontend.py
# 
# File Description: A module to allow connection to the new Akrios Front End.
#
# Dependencies: You will need to 'pip3 install websocket-client' to use this module.
#
#
# Implemented features:
#
#
"""
    Module used to communicate with Akrios front end.

    Classes:
        FEReceivedMessage is used to parse incoming JSON messages from the front end.
        __init__(self, message, fesock)
            message is the JSON from the front end
            fesock is the instance of FESocket for tracking players

        FESocket is used to authenticate to and send messages to the front en d.
        __init__(self)
"""

import json
import logging
import socket
import time
from websocket import WebSocket

import comm
import event
from keys import FRONT_END

log = logging.getLogger(__name__)

fesocket = None


class FEReceivedMessage(object):
    def __init__(self, message_, fesock):
        super().__init__()

        log.debug(f'Received message from front end: {message_}')
        self.message = json.loads(message_)

        # Point an instance attribute to the module level front end socket.
        # Used for adding to and removing refs
        self.fesock = fesock

        # When we receive a JSON message from the front end it will always have an event type.
        self.rcvr_func = {'heartbeat': (self.fesock.msg_gen_heartbeat, None),
                          'restart': (self.received_restart, None),
                          'player/input': (self.received_player_input, None),
                          'game/load_players': (self.received_game_load_players, None),
                          'connection/connected': (self.received_connection_connected, None),
                          'connection/disconnected': (self.received_connection_disconnected, None)}

        self.restart_downtime = 0

    def parse_frame(self):
        """
            Parse any received JSON from the Front End.

            Verify we have an attribute from the JSON that is 'event'. If we have a key
            in the rcvr_func that matches we will execute.

            return whatever is returned by the method, or None.
       """
        if 'event' in self.message and self.message['event'] in self.rcvr_func:
            exec_func, args = self.rcvr_func[self.message['event']]
            if args is None:
                retvalue = exec_func()
            else:
                retvalue = exec_func(args)

            if retvalue:
                return retvalue

    def is_event_status(self, status):
        """
            A helper method to determine if the event we received is type of status.

            return True/False
        """
        if 'event' in self.message and 'status' in self.message:
            if self.message['status'] == status:
                return True
            else:
                return False

    def received_restart(self):
        """
        We received a restart event. We'll assign the value to the restart_downtime
        attribute for access by the calling code.
        """
        if 'payload' in self.message:
            self.restart_downtime = int(self.message['payload']['downtime'])

    def received_player_input(self):
        """
        We received input from a player.
        """
        if 'payload' in self.message:
            uuid = self.message['payload']['uuid']
            addr = self.message['payload']['addr']
            port = self.message['payload']['port']
            msg = self.message['payload']['msg']

            log.debug(f"Received front end message: {uuid}@{addr}:{port} '{msg}'")
            return uuid, addr, port, msg

    def received_connection_connected(self):
        """
        We received a notification of a new connection.
        """
        if 'payload' in self.message:
            uuid = self.message['payload']['uuid']
            addr = self.message['payload']['addr']
            port = self.message['payload']['port']

            log.info(f'Received connection connected: {uuid}@{addr}')
            return uuid, addr, port

    def received_connection_disconnected(self):
        """
        We received a notification of a client disconnect.
        """
        if 'payload' in self.message:
            uuid = self.message['payload']['uuid']
            addr = self.message['payload']['addr']
            port = self.message['payload']['port']

            log.info(f'Received client disconnect: {uuid}@{addr}')
            return uuid, addr, port

    def received_game_load_players(self):
        """
        We should receive this after a 'softboot'.
        We have notified the front end of a soft boot, it should have restarted us.
        When the game connects to the front end, if there is a list of sessions that means
        we have soft booted, so we're receiving a list of session ID's and player names to log in.
        """
        if 'payload' in self.message:
            players_dict = self.message['payload']['players']

            log.info(f'Received session->player dict after startup: {players_dict}')
            return players_dict


class FESocket(WebSocket):
    def __init__(self):
        super().__init__(sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))

        self.inbound_frame_buffer = []
        self.outbound_frame_buffer = []

        self.events = event.Queue(self, 'frontend')

        self.state = {'connected': False,
                      'disconnected': False,
                      'coldboot': False,
                      'unknown': False}

        event.init_events_frontend(self)

        self.last_heartbeat = 0

    def fesocket_connect(self):
        try:
            result = self.connect('ws://localhost:8989')
            comm.wiznet('fesocket_connect: Attempting connection to front end.')
            comm.wiznet(f'fesocket_connect result: {result}')
        except ConnectionError or ConnectionRefusedError or ConnectionAbortedError as err:
            log.error(f'Exception raised in fesocket_connect: {err}')
            return False
        # We need to set the below on the socket as websocket.WebSocket is
        # blocking by default.  :(
        self.sock.setblocking(0)
        self.state['connected'] = True
        return True

    def fesocket_disconnect(self):
        comm.wiznet('fesocket_disconnect: Disconnecting from front end.')
        self.handle_write()
        self.state['connected'] = False
        self.state['authenticated'] = False
        self.inbound_frame_buffer.clear()
        self.outbound_frame_buffer.clear()
        self.events.clear()
        self.close()

    def send_out(self, frame):
        """
        A generic to make writing out cleaner, nothing more.
        """
        self.outbound_frame_buffer.append(frame)

    def read_in(self):
        """
        A generic to make reading in cleaner, nothing more.
        """
        return self.inbound_frame_buffer.pop(0)

    def msg_gen_heartbeat(self):
        """
        Once connected to the front end we will receive regular heartbeats.
        """
        self.last_heartbeat = time.time()

        msg = {'event': 'heartbeat',
               'secret': FRONT_END}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_output(self, msg_, session_uuid):
        """
        Test msg generator to confirm receipt of message by echo
        """
        payload = {'message': msg_,
                   'uuid': session_uuid}

        msg = {'event': 'players/output',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_login(self, player_name, uuid_):
        """
        Notify the front end of a successful player login.
        """
        payload = {'name': player_name,
                   'uuid': uuid_}
        msg = {'event': 'players/sign-in',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_logout(self, player_name, uuid_):
        """
        Notify the front end of a player logout.
        """
        payload = {'name': player_name,
                   'uuid': uuid_}
        msg = {'event': 'players/sign-out',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_login_failed(self, player_name, uuid_):
        """
        Notify the front end of a player failed login, "wrong password".
        """
        payload = {'name': player_name,
                   'uuid': uuid_}
        msg = {'event': 'players/login-failed',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_game_softboot(self, wait_time=10):
        """
        Notify the front end the game is going down for softboot.
        """
        payload = {'wait_time': wait_time}
        msg = {'event': 'game/softboot',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_do_client_echo(self, uuid_):
        """
        Notify the front end to send a 'do echo' to clients (where appropriate).
        """
        payload = {'command': 'do echo',
                   'uuid': uuid_}
        msg = {'event': 'player/session command',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_dont_client_echo(self, uuid_):
        """
        Notify the front end to send a 'dont echo' to clients (where appropriate).
        """
        payload = {'command': 'dont echo',
                   'uuid': uuid_}
        msg = {'event': 'player/session command',
               'secret': FRONT_END,
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def handle_read(self):
        """
        Perform the actual socket read attempt. Append anything received to the inbound
        buffer.
        """
        try:
            self.inbound_frame_buffer.append(self.recv())
            log.debug(f'Front End In: {self.inbound_frame_buffer[-1]}')
        except Exception as err:
            log.debug(f'Front End Exception raised in handle_read: {err}')

    def handle_write(self):
        """
        Perform a write out to the front end from the outbound buffer.
        """
        try:
            outdata = self.outbound_frame_buffer.pop(0)
            if outdata is not None:
                self.send(outdata)
                log.debug(f'Front End Out: {outdata}')
        except Exception as err:
            log.debug(f'Error sending data frame to Front End: {err}')

    def receive_message(self):
        """
        Attempt a read in from the Front End
        """
        try:
            return FEReceivedMessage(self.read_in(), self)
        except Exception as err:
            log.debug(f'Error receiving message from Front End: {err}')
