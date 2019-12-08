#! usr/bin/env python3
# Project: Akrios
# Filename: grapevine.py
# 
# File Description: A module to allow connection to Grapevine chat network.
#                   Visit https://www.grapevine.haus/
#
# Dependencies: You will need to 'pip3 install websocket-client' to use this module.
#
#
# Implemented features:
#       Authentication to the grapevine network.
#       Registration to the Gossip Channel(default) or other channels.
#       Restart messages from the grapevine network.
#       Sending and receiving messages to the Gossip(default) or other channel.
#       Sending and receiving Player sign-in/sign-out messages.
#       Player sending and receiving Tells.
#       Sending and receiving player status requests.
#       Sending single game requests.
#       Game connect and disconnect messages.
#       Sending and receiving game status requests.
#       Game Status (all connected games, and single game)
#       Achievements (Sync, Creation, update, deletion)
#
#
# Example usage would be to import this module into your main game server.  During server startup
# assign grapevine.gsocket to grapevine.GrapevineSocket().  After instance init is when you need
# to connect via grapevine.gsocket.gsocket_connect().  PLEASE PUT YOUR CLIENT ID AND CLIENT SECRET
# into the appropriate instance attributes of GrapevineSocket below.
#
# You will need to periodically call the gsocket.handle_read() and gsocket.handle_write() as
# required by your configuration.   Please see the examples in the repo of how this might look
# for you.
#
#
# Please see additional code examples of commands, events, etc in the repo.
# https://github.com/oestrich/gossip-clients
#
# Or visit the latest version of the live client at:
# https://github.com/bdubyapee/akriosmud
#
# By: Jubelo, Creator of AkriosMUD
# At: akriosmud.funcity.org:5678
#     jubelo@akriosmud.funcity.org
# 

"""
    Module used to communicate with the Grapevine.haus chat+ network.
    https://grapevine.haus
    https://vineyard.haus

    Classes:
        GrapevineReceivedMessage is used to parse incoming JSON messages from the network.
        __init__(self, message, gsock)
            message is the JSON from the grapevine network
            gsock is the instance of GrapevineSocket for tracking foreign players locally

        GrapevineSocket is used to authenticate to and send messages to the grapevine network.
        __init__(self)

"""

import datetime
import json
import logging
import socket
import time
import uuid
from websocket import WebSocket

import comm
import event
from keys import LIVE, CLIENT_ID, SECRET_KEY
import player

log = logging.getLogger(__name__)

gsocket = None


class GrapevineReceivedMessage(object):
    def __init__(self, message_, gsock):
        super().__init__()

        # Short hand to convert JSON data to instance attributes.
        # Not secure at all.  If you're worried about it feel free to modify
        # to your needs.
        log.debug(f'Received message from Grapevine: {message_}')
        self.message = json.loads(message_)

        # Point an instance attribute to the module level grapevine socket.
        # Used for adding to and removing refs as well as keeping the foreign player
        # cache in the gsocket up to date.
        self.gsock = gsock

        # When we receive a JSON message from grapevine it will always have an event type.
        self.rcvr_func = {'heartbeat': (self.gsock.msg_gen_heartbeat, None),
                          'authenticate': (self.received_auth, None),
                          'restart': (self.received_restart, None),
                          'channels/broadcast': (self.received_broadcast_message, None),
                          'channels/subscribe': (self.received_chan_sub, gsock.sent_refs),
                          'channels/unsubscribe': (self.received_chan_unsub, gsock.sent_refs),
                          'players/sign-out': (self.received_player_logout, gsock.sent_refs),
                          'players/sign-in': (self.received_player_login, gsock.sent_refs),
                          'games/connect': (self.received_games_connected, None),
                          'games/disconnect': (self.received_games_disconnected, None),
                          'games/status': (self.received_games_status, gsock.sent_refs),
                          'players/status': (self.received_player_status, gsock.sent_refs),
                          'tells/send': (self.received_tells_status, gsock.sent_refs),
                          'tells/receive': (self.received_tells_message, None),
                          'channels/send': (self.received_message_confirm, gsock.sent_refs),
                          'achievements/sync': (self.received_achievements_sync, gsock.sent_refs),
                          'achievements/create': (self.received_achievements_create, gsock.sent_refs),
                          'achievements/update': (self.received_achievements_update, gsock.sent_refs),
                          'achievements/delete': (self.received_achievements_delete, gsock.sent_refs)}

        self.restart_downtime = 0
        self.achievements = {}
        self.total_achievements = 0

    def parse_frame(self):
        """
            Parse any received JSON from the Grapevine network.

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

    def received_auth(self):
        """
            We received an event Auth event type.
            Determine if we are already authenticated, if so subscribe to the channels
            as determined in msg_gen_chan_subscribed in the GrapevineSocket Object.
            Otherwise, if we are not authenticated yet we send another authentication attempt
            via msg_gen_authenticate().  This is in place for path hiccups or restart events.

            Grapevine 1.0.0
        """
        if self.is_event_status('success'):
            self.gsock.state['authenticated'] = True
            self.gsock.state['connected'] = True
            self.gsock.msg_gen_chan_subscribe()
            comm.wiznet('Received authentication success from Grapevine.')
            self.gsock.msg_gen_player_status_query()
            comm.wiznet('Sending player status query to all Grapevine games.')
        elif not self.gsock.state['authenticated']:
            comm.wiznet('received_auth: Sending Authentication message to Grapevine.')
            self.gsock.msg_gen_authenticate()

    def received_restart(self):
        """
        We received a restart event. We'll assign the value to the restart_downtime
        attribute for access by the calling code.

        Grapevine 1.0.0
        """
        if 'payload' in self.message:
            self.restart_downtime = int(self.message['payload']['downtime'])

    def received_chan_sub(self, sent_refs):
        """
        We have attempted to subscribe to a channel.  This is a response message from Grapevine.
        If failure, we make sure we show unsubscribed in our local list.
        if success, we make sure we show subscribed in our local list.

        Grapevine 1.0.0
        """
        if 'ref' in self.message and self.message['ref'] in sent_refs:
            orig_req = sent_refs.pop(self.message['ref'])
            if self.is_event_status('failure'):
                channel = orig_req['payload']['channel']
                self.gsock.subscribed[channel] = False
                comm.wiznet(f"Grapevine failed to subscribe to channel {channel}")
            elif self.is_event_status('success'):
                channel = orig_req['payload']['channel']
                self.gsock.subscribed[channel] = True
                comm.wiznet(f"Grapevine successfully subscribed to channel {channel}")

    def received_chan_unsub(self, sent_refs):
        """
        We at some point sent a channel unsubscribe. This is verifying Grapevine
        received that.  We unsub in our local list.

        Grapevine 1.0.0
        """
        if 'ref' in self.message and self.message['ref'] in sent_refs:
            orig_req = sent_refs.pop(self.message['ref'])
            channel = orig_req['payload']['channel']
            self.gsock.subscribed[channel] = False
            comm.wiznet(f"Grapevine unsubscribed from channel {channel}")

    def received_player_logout(self, sent_refs):
        """
        We have received a "player/sign-out" message from Grapevine.

        Determine if it is a success message, which is an indication to us that Grapevine
        received a player logout from us and is acknowledging, or if it is a message from
        another game on the Grapevine network.

        return None if it's an ack from grapevine, return player info if it's foreign.

        Grapevine 1.0.0
        """
        if 'ref' in self.message:
            # We are a success message from Grapevine returned from our notification.
            if self.message['ref'] in sent_refs and self.is_event_status('success'):
                sent_refs.pop(self.message['ref'])
                return
            # We are receiving a player logout from another game.
            if 'game' in self.message['payload']:
                game = self.message['payload']['game'].capitalize()
                player_ = self.message['payload']['name'].capitalize()
                if game in self.gsock.other_games_players:
                    if player_ in self.gsock.other_games_players[game]:
                        self.gsock.other_games_players[game].remove(player_)
                    if len(self.gsock.other_games_players[game]) <= 0:
                        self.gsock.other_games_players.pop(game)

                return player_, 'signed out of', game

    def received_player_login(self, sent_refs):
        """
        We have received a "player/sign-in" message from Grapevine.

        Determine if it is a success message, which is an indication to us that Grapevine
        received a player login from us and is acknowledging, or if it is a message from
        another game on the Grapevine Network.

        return None if it's an ack from grapevine, return player info if it's foreign

        Grapevine 1.0.0
        """
        if 'ref' in self.message:
            if self.message['ref'] in sent_refs and self.is_event_status('success'):
                sent_refs.pop(self.message['ref'])
                return
            if 'game' in self.message['payload']:
                game = self.message['payload']['game'].capitalize()
                player_ = self.message['payload']['name'].capitalize()
                if game in self.gsock.other_games_players:
                    if player_ not in self.gsock.other_games_players[game]:
                        self.gsock.other_games_players[game].append(player_)
                else:
                    self.gsock.other_games_players[game] = []
                    self.gsock.other_games_players[game].append(player_)

                return player_, 'signed into', game

    def received_player_status(self, sent_refs):
        """
        We have requested a multi-game or single game status update.
        This is the response. We pop the valid Ref from our local list
        and add them to the local cache.

        Grapevine 1.1.0
        """
        if 'ref' in self.message and 'payload' in self.message:
            # On first receive we pop the ref just so it's gone from the queue
            if self.message['ref'] in sent_refs:
                sent_refs.pop(self.message['ref'])

            game = self.message['payload']['game'].capitalize()

            if len(self.message['payload']['players']) == 1 and self.message['payload']['players'] in ['', None]:
                self.gsock.other_games_players[game] = []
                return
            if len(self.message['payload']['players']) == 1:
                player_ = self.message['payload']['players'][0].capitalize()
                self.gsock.other_games_players[game] = []
                self.gsock.other_games_players[game].append(player_)
                return
            if len(self.message['payload']['players']) > 1:
                player_ = [player_.capitalize() for player_ in self.message['payload']['players']]
                self.gsock.other_games_players[game] = []
                self.gsock.other_games_players[game] = player_
                return

    def received_tells_status(self, sent_refs):
        """
        One of the local players has sent a tell.  This is specific response of an error.
        Provide the error and other pertinent info to the local game for handling
        as required.

        Grapevine 2.0.0
        """
        if 'ref' in self.message:
            if self.message['ref'] in sent_refs and 'error' in self.message:
                orig_req = sent_refs.pop(self.message['ref'])
                if self.is_event_status('failure'):
                    caller = orig_req['payload']['from_name'].capitalize()
                    target = orig_req['payload']['to_name'].capitalize()
                    game = orig_req['payload']['to_game'].capitalize()
                    return caller, target, game, self.message['error']

    def received_tells_message(self):
        """
        We have received a tell message destined for a player in our game.
        Grab the details and return to the local game to handle as required.

        Grapevine 2.0.0
        """
        if 'ref' in self.message and 'payload' in self.message:
            sender = self.message['payload']['from_name']
            target = self.message['payload']['to_name']
            game = self.message['payload']['from_game']
            sent = self.message['payload']['sent_at']
            message = self.message['payload']['message']

            log.info(f"Grapevine received tell: {sender}@{game} told {target} '{message}'")
            return sender, target, game, sent, message

    def received_games_status(self, sent_refs):
        """
        Received a game status response.  Return the received info to the local
        game to handle as required.

        Grapevine 2.1.0
        """
        if 'ref' in self.message and 'payload' in self.message and self.is_event_status("success"):
            sent_refs.pop(self.message['ref'])
            if self.message['ref'] in sent_refs:
                game = self.message['payload']['game']
                display_name = self.message['payload']['display_name']
                description = self.message['payload']['description']
                homepage = self.message['payload']['homepage_url']
                user_agent = self.message['payload']['user_agent']
                user_agent_repo = self.message['payload']['user_agent_repo_url']
                connections = self.message['payload']['connections']

                supports = self.message['payload']['supports']
                num_players = self.message['payload']['players_online_count']

                return (game, display_name, description, homepage, user_agent,
                        user_agent_repo, connections, supports, num_players)

        if 'ref' in self.message and 'error' in self.message and self.is_event_status('failure'):
            orig_req = sent_refs.pop(self.message['ref'])
            if self.message['ref'] in sent_refs:
                game = orig_req['payload']['game']
                return game, self.message['error']

    def received_message_confirm(self, sent_refs):
        """
        We received a confirmation that Grapevine received an outbound broadcast message
        from us.  Nothing to see here other than removing from our sent references list.

        Grapevine : Should be semi version neutral.
        """
        if 'ref' in self.message:
            if self.message['ref'] in sent_refs and self.is_event_status('success'):
                sent_refs.pop(self.message['ref'])

    def is_other_game_player_update(self):
        """
        A helper method to determine if this is a player update from another game.
        """
        if 'event' in self.message:
            if self.message['event'] == 'players/sign-in' or self.message['event'] == 'players/sign-out':
                if 'payload' in self.message and 'game' in self.message['payload']:
                    return True
            else:
                return False

    def received_games_connected(self):
        """
        A foreign game has connected to the network, add the game to our local
        cache of games/players and send a request for player list.

        Grapevine 2.2.0
        """
        if 'payload' in self.message:
            # Clear what we knew about this game and request an update.
            # Requesting updates from all games at this point, might as well refresh
            # as I'm sure some games don't implement all features like player sign-in
            # and sign-outs.
            self.gsock.other_games_players[self.message['payload']['game']] = []
            self.gsock.msg_gen_player_status_query()
            return self.message['payload']['game']

    def received_games_disconnected(self):
        """
        A foreign game has disconnected, remove it from our local cache and return
        details to local game to handle as required.

        Grapevine 2.2.0
        """
        if 'payload' in self.message:
            if self.message['payload']['game'] in self.gsock.other_games_players:
                self.gsock.other_games_players.pop(self.message['payload']['game'])
            return self.message['payload']['game']

    def received_broadcast_message(self):
        """
        We received a broadcast message from another game.  Return the pertinent
        info so the local game can handle as required.  See examples above.

        Grapevine 1.0.0
        """
        if 'payload' in self.message:
            name = self.message['payload']['name']
            game = self.message['payload']['game']
            message = self.message['payload']['message']
            channel = self.message['payload']['channel']

            log.info(f"Grapevine received message: {name}@{game} on {channel} said '{message}'")
            return name, game, message, channel

    def received_achievements_sync(self, sent_refs):
        """
        We have received an achievements sync response.
        Grab the details and update the achievements attribute.

        Grapevine 2.3.0
        """
        if 'ref' in self.message and 'payload' in self.message:
            if self.message['ref'] in sent_refs:
                sent_refs.pop(self.message['ref'])
            self.total_achievements = self.message['payload']['total']
            all_achievements = self.message['payload']['achievements']

            for each_achievement in all_achievements:
                self.achievements[each_achievement['key']] = each_achievement

    def received_achievements_create(self, sent_refs):
        """
        We have received an achievements create response.
        Grab the details and update the achievements attribute.

        Grapevine 2.3.0
        """
        if 'ref' in self.message and 'payload' in self.message and 'status' in self.message:
            if self.message['ref'] in sent_refs:
                sent_refs.pop(self.message['ref'])
            if self.message['status'] == 'success':
                if self.message['payload']['key'] not in self.achievements:
                    self.achievements['key'] = self.message['payload']
                    return
            elif self.message['status'] == 'failure':
                return self.message['payload']['errors']

    def received_achievements_update(self, sent_refs):
        """
        We have received an achievements update response.
        Grab the details and update the achievements attribute.

        Grapevine 2.3.0
        """
        if 'ref' in self.message and 'payload' in self.message and 'status' in self.message:
            if self.message['ref'] in sent_refs:
                sent_refs.pop(self.message['ref'])
            if self.message['status'] == 'success':
                if self.message['payload']['key'] not in self.achievements:
                    self.achievements['key'] = self.message['payload']
                    return
            elif self.message['status'] == 'failure':
                return self.message['payload']['errors']

    def received_achievements_delete(self, sent_refs):
        """
        We have received an achievements update response.
        Grab the details and update the achievements attribute.

        Grapevine 2.3.0
        """
        if 'ref' in self.message and 'payload' in self.message and 'status' in self.message:
            if self.message['ref'] in sent_refs:
                sent_refs.pop(self.message['ref'])
            if self.message['status'] == 'success':
                if self.message['payload']['key'] in self.achievements:
                    self.achievements.pop(self.message['payload']['key'])
                    return


class GrapevineSocket(WebSocket):
    def __init__(self):
        super().__init__(sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))

        self.inbound_frame_buffer = []
        self.outbound_frame_buffer = []

        self.events = event.Queue(self, 'grapevine')

        self.client_id = CLIENT_ID
        self.client_secret = SECRET_KEY
        self.supports = ['channels', 'games', 'players', 'tells']

        # Populate the channels attribute if you want to subscribe to a specific
        # channel or channels during authentication.
        self.channels = ['gossip']
        self.version = '2.3.0'
        self.user_agent = 'AkriosMUD v0.4.5'

        self.state = {'connected': False,
                      'authenticated': False}

        self.subscribed = {'gossip': True}

        event.init_events_grapevine(self)

        self.sent_refs = {}

        # The below is a cache of players we know about from other games.
        # Right now I just use this to populate additional fields in our in-game 'who' command
        # to also show players logged into other Grapevine connected games.
        self.other_games_players = {}

        # The below is to track the last time we received a heartbeat from Grapevine.
        self.last_heartbeat = 0

    def gsocket_connect(self):
        try:
            result = self.connect('wss://grapevine.haus/socket')
            comm.wiznet('gsocket_connect: Attempting connection to Grapevine.')
            comm.wiznet(f'gsocket_connect result: {result}')
        except ConnectionError or ConnectionRefusedError or ConnectionAbortedError as err:
            log.error(f'Exception raised in gsocket_connect: {err}')
            return False
        # We need to set the below on the socket as websocket.WebSocket is
        # blocking by default.  :(
        self.sock.setblocking(0)
        self.msg_gen_authenticate()

        comm.wiznet('gsocket_connect: Sending Auth to Grapevine Network.')
        return True

    def gsocket_disconnect(self):
        comm.wiznet('gsocket_disconnect: Disconnecting from Grapevine Network.')
        self.state['connected'] = False
        self.state['authenticated'] = False
        self.inbound_frame_buffer.clear()
        self.outbound_frame_buffer.clear()
        self.events.clear()
        self.subscribed.clear()
        self.other_games_players.clear()
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

    def msg_gen_authenticate(self):
        """
        Need to authenticate to the Grapevine.haus network to participate.
        This creates and sends that authentication as well as defaults us to
        an authenticated state unless we get an error back indicating otherwise.

        Grapevine 1.0.0
        """
        payload = {'client_id': self.client_id,
                   'client_secret': self.client_secret,
                   'supports': self.supports,
                   'channels': self.channels,
                   'version': self.version,
                   'user_agent': self.user_agent}

        # If we haven't assigned any channels, lets pull that out of our auth
        # so we aren't trying to auth to an empty string.  This also causes us
        # to receive an error back from Grapevine.
        if not self.channels:
            payload.pop('channels')

        msg = {'event': 'authenticate',
               'payload': payload}

        self.state['authenticated'] = True

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_heartbeat(self):
        """
        Once registered to Grapevine we will receive regular heartbeats.  The
        docs indicate to respond with the below heartbeat response which
        also provides an update player logged in list to the network.

        Grapevine 1.0.0
        """
        # The below line builds a list of player names logged into Akrios for sending
        # in response to a grapevine heartbeat.
        player_list = [player_.name.capitalize() for player_ in player.playerlist]

        self.last_heartbeat = time.time()

        payload = {'players': player_list}
        msg = {'event': 'heartbeat',
               'payload': payload}

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_chan_subscribe(self, chan=None):
        """
        Subscribe to a specific channel, or Gossip by default.

        Grapevine 1.0.0
        """
        ref = str(uuid.uuid4())
        if chan is None or not chan:
            payload = {'channel': 'gossip'}
        else:
            payload = {'channel': chan}

        if payload['channel'] in self.subscribed:
            return

        msg = {'event': 'channels/subscribe',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_chan_unsubscribe(self, chan=None):
        """
        Unsubscribe from a specific channel, default to Gossip channel if
        none given.

        Grapevine 1.0.0
        """
        ref = str(uuid.uuid4())
        if not chan:
            payload = {'channel': 'gossip'}
        else:
            payload = {'channel': chan}

        msg = {'event': 'channels/unsubscribe',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_login(self, player_name):
        """
        Notify the Grapevine network of a player login.

        Grapevine 1.0.0
        """
        ref = str(uuid.uuid4())
        payload = {'name': player_name.capitalize()}
        msg = {'event': 'players/sign-in',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_logout(self, player_name):
        """
        Notify the Grapevine network of a player logout.

        Grapevine 1.0.0
        """
        ref = str(uuid.uuid4())
        payload = {'name': player_name.capitalize()}
        msg = {'event': 'players/sign-out',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_message_channel_send(self, caller, channel, message):
        """
        Sends a channel message to the Grapevine network.  If we're not showing
        as subscribed on our end, we bail out.

        Grapevine 1.0.0
        """
        if channel not in self.subscribed:
            return

        ref = str(uuid.uuid4())
        payload = {'channel': channel,
                   'name': caller.disp_name,
                   'message': message[:290]}
        msg = {'event': 'channels/send',
               'ref': ref,
               'payload': payload}

        log.info(f"Grapevine message: {caller.disp_name} on {channel} said '{message}'")

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_game_all_status_query(self):
        """
        Request for all games to send full status update.  You will receive in
        return from each game quite a bit of detailed information.  See the
        grapevine.haus Documentation or review the receiver code above.

        Grapevine 2.1.0
        """
        ref = str(uuid.uuid4())

        msg = {'events': 'games/status',
               'ref': ref}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_game_single_status_query(self, game):
        """
        Request for a single game to send full status update.  You will receive in
        return from each game quite a bit of detailed information.  See the
        grapevine.haus Documentation or review the receiver code above.

        Grapevine 2.1.0
        """
        ref = str(uuid.uuid4())

        msg = {'events': 'games/status',
               'ref': ref,
               'payload': {'game': game}}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_status_query(self):
        """
        This requests a player list status update from all connected games.

        Grapevine 1.1.0
        """
        ref = str(uuid.uuid4())

        msg = {'event': 'players/status',
               'ref': ref}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_single_status_query(self, game):
        """
        Request a player list status update from a single connected game.

        Grapevine 1.1.0
        """
        ref = str(uuid.uuid4())

        msg = {'events': 'players/status',
               'ref': ref,
               'payload': {'game': game}}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_player_tells(self, caller_name, game, target, message):
        """
        Send a tell message to a player on the Grapevine network.

        Grapevine 2.0.0
        """
        game = game.capitalize()
        target = target.capitalize()

        ref = str(uuid.uuid4())
        time_now = f'{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}Z'
        payload = {'from_name': caller_name,
                   'to_game': game,
                   'to_name': target,
                   'sent_at': time_now,
                   'message': message[:290]}

        msg = {'event': 'tells/send',
               'ref': ref,
               'payload': payload}

        log.info(f"Grapevine tell: {caller_name} to {target}@{game} said '{message}'")

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_achievements_sync(self):
        """
        Request the list of achievements for our game.

        Grapevine 2.3.0
        """
        ref = str(uuid.uuid4())

        msg = {'events': 'achievements/sync',
               'ref': ref}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_achievements_create(self, title='Generic Title', desc='Generic Description',
                                    points=10, display=False, partial=False, total=None):
        """
        Create a new achievement.

        The payload should contain all of the attributes of an achievement that you wish to
        set.  I have included all fields possible below for reference.

        Grapevine 2.3.0
        """
        ref = str(uuid.uuid4())

        payload = {'title': title,
                   'description': desc,
                   'points': points,
                   'display': display,
                   'partial_progress': partial,
                   'total_progress': total}

        msg = {'events': 'achievements/create',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_achievements_update(self, key, title='Generic Title', desc='Generic Description',
                                    points=0, display=False, partial=False, total=None):
        """
        Update an existing achievement

        Per the documentation we utilize the same event type of 'achievements/create' and include
        the unique key in the payload.  You only need to provide the payload fields you wish to
        update.  We have included all fields possible below for reference.  Modify for your needs.

        Grapevine 2.3.0
        """
        ref = str(uuid.uuid4())

        payload = {'key': key,
                   'title': title,
                   'description': desc,
                   'points': points,
                   'display': display,
                   'partial_progress': partial,
                   'total_progress': total}

        msg = {'events': 'achievements/update',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def msg_gen_achievements_delete(self, key):
        """
        Delete an existing achievement.

        Provide the unique key for the achievement, provide as the payload to delete
        the achievement on Grapevine.

        Grapevine 2.3.0
        """
        ref = str(uuid.uuid4())

        payload = {'key': key}

        msg = {'events': 'achievements/delete',
               'ref': ref,
               'payload': payload}

        self.sent_refs[ref] = msg

        self.send_out(json.dumps(msg, sort_keys=True, indent=4))

    def handle_read(self):
        """
        Perform the actual socket read attempt. Append anything received to the inbound
        buffer.
        """
        try:
            self.inbound_frame_buffer.append(self.recv())
            log.debug(f'Grapevine In: {self.inbound_frame_buffer[-1]}')
        except Exception as err:
            log.debug(f'Exception raised in handle_read: {err}')

    def handle_write(self):
        """
        Perform a write out to Grapevine from the outbound buffer.
        """
        try:
            outdata = self.outbound_frame_buffer.pop(0)
            if outdata is not None:
                self.send(outdata)
                log.debug(f'Grapevine Out: {outdata}')
        except Exception as err:
            log.debug(f'Error sending data frame to Grapevine: {err}')

    def receive_message(self):
        """
        Attempt a read in from Grapevine.
        """
        try:
            return GrapevineReceivedMessage(self.read_in(), self)
        except Exception as err:
            log.debug(f'Error receiving message from Grapevine: {err}')
