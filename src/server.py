#! usr/bin/env python
# Project: Dark Waters
# Filename: server.py
# 
# File Description: The main server module.
# 
# By: Jubelo

# Standard Library
import argparse
import asyncio
import logging
import signal
import string
from typing import Dict, List

# Third Party

# Project
import area
import color
import comm
import event
import frontend
import grapevine
import helpsys
import login
import player
import races
import status
from world import serverlog

log = logging.getLogger(__name__)

# This is the dict of connected sessions.
sessions = {}

# Assistant variables for removing certain characters from our input.
valid_chars = string.printable.replace(string.whitespace[1:], "")


class Session(object):
    def __init__(self, uuid, address, port, name=None):
        self.owner = None
        self.host = address
        self.port = port
        self.session = uuid
        self.ansi = True
        self.promptable = False
        self.in_buf = asyncio.Queue()
        self.out_buf = asyncio.Queue()
        self.state = {'connected': True,
                      'link dead': False,
                      'logged in': False}
        sessions[self.session] = self

        asyncio.create_task(self.read(), name=self.session)
        asyncio.create_task(self.send(), name=self.session)

        self.login(name)

    def handle_close(self):
        asyncio.create_task(frontend.msg_gen_player_logout(self.owner.name.capitalize(), self.session))
        self.state['connected'] = False
        self.state['logged in'] = False
        for tasks in asyncio.all_tasks():
            if self.session == tasks.get_name():
                tasks.cancel()

    def login(self, name):
        if name:
            new_conn = login.Login(name, softboot=True)
        else:
            new_conn = login.Login()
        new_conn.sock = self
        new_conn.sock.owner = new_conn
        if not name:
            new_conn.greeting()
            comm.wiznet(f"Accepting connection from: {new_conn.sock.host}")
        else:
            new_conn.interp = new_conn.character_login
            new_conn.interp()

    def dispatch(self, msg, trail=True):
        if self.state['connected']:
            asyncio.create_task(self.a_dispatch(msg, trail), name=self.session)

    async def a_dispatch(self, msg, trail=True):
        if trail:
            msg = f'{msg}\n\r'
        if self.ansi:
            msg = color.colorize(msg)
        else:
            msg = color.decolorize(msg)
        asyncio.create_task(self.out_buf.put(msg), name=self.session)

    async def write(self):
        if self.state['logged in']:
            if hasattr(self.owner, "editing"):
                asyncio.create_task(self.out_buf.put(">"))
            elif self.promptable:
                if self.owner.oocflags["afk"]:
                    pretext = "{W[{RAFK{W]{x "
                else:
                    pretext = ""
                output = color.colorize(f"\n\r{pretext}{self.owner.prompt}\n\r")
                asyncio.create_task(self.out_buf.put(output), name=self.session)

    async def send(self):
        while self.state['connected']:
            message = await self.out_buf.get()
            asyncio.create_task(frontend.msg_gen_player_output(message, self.session),
                                name=self.session)

    async def read(self):
        while self.state['connected']:
            message = await self.in_buf.get()
            self.owner.interp(message)


async def shutdown(signal_: signal.Signals, loop_: asyncio.AbstractEventLoop) -> None:
    """
        shutdown coroutine utilized for cleanup on receipt of certain signals.
        Created and added as a handler to the loop in __main__

        https://www.roguelynn.com/talks/
    """
    log.warning(f'Received exit signal {signal_.name}')

    tasks: List[asyncio.Task] = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    log.info(f'Cancelling {len(tasks)} outstanding tasks')

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop_.stop()


def handle_exception_generic(loop_: asyncio.AbstractEventLoop, context: Dict) -> None:
    msg: str = context.get('exception', context['message'])
    log.warning(f'Caught exception: {msg} in loop: {loop_}')
    log.warning(f'Caught in task: {asyncio.current_task().get_name()}')  # type: ignore


async def handle_messages() -> None:
    while status.server['running']:
        message = await frontend.messages_to_game.get()
        session, msg = message
        if session in sessions:
            asyncio.create_task(sessions[session].in_buf.put(msg))


async def cmd_client_connected(options) -> None:
    uuid, address, port = options
    Session(uuid, address, port)


async def cmd_client_disconnected(options) -> None:
    uuid, address, port = options
    if uuid in sessions:
        sessions[uuid].status['link dead'] = True


async def cmd_game_load_players(options) -> None:
    for session in options:
        name, address, port = options[session]
        Session(session, address, port, name)


async def handle_commands() -> None:
    commands = {'client_connected': cmd_client_connected,
                'client_disconnected': cmd_client_disconnected,
                'game_load_players': cmd_game_load_players}

    while status.server['running']:
        command = await frontend.commands_to_game.get()
        command_type, options = command
        if command_type in commands:
            asyncio.create_task(commands[command_type](options))


async def cmd_grapevine_tells_send(message):
    caller, target, game, error_msg = message
    message = (f"\n\r{{GGrapevine Tell to {{y{target}@{game}{{G "
               f"returned an Error{{x: {{R{error_msg}{{x")
    for eachplayer in player.playerlist:
        if eachplayer.disp_name == caller:
            if eachplayer.oocflags_stored['grapevine'] == 'true':
                eachplayer.write(message)
                return


async def cmd_grapevine_tells_receive(message):
    sender, target, game, sent, message = message
    message = (f"\n\r{{GGrapevine Tell from {{y{sender}@{game}{{x: "
               f"{{G{message}{{x.\n\rReceived at : {sent}.")
    for eachplayer in player.playerlist:
        if eachplayer.disp_name == target.capitalize():
            if eachplayer.oocflags_stored['grapevine'] == 'true':
                eachplayer.write(message)
                return


async def cmd_grapevine_games_connect(message):
    game = message.capitalize()
    message = f"\n\r{{GGrapevine Status Update: {game} connected to network{{x"

    if message != "":
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for eachplayer in grape_enabled:
            eachplayer.write(message)


async def cmd_grapevine_games_disconnect(message):
    game = message.capitalize()
    message = f"\n\r{{GGrapevine Status Update: {game} disconnected from network{{x"
    if message != "":
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for eachplayer in grape_enabled:
            eachplayer.write(message)


async def cmd_grapevine_channels_broadcast(message):
    name, game, message, channel = message
    if name is None or game is None:
        comm.wiznet("Received channels/broadcast with None type")
        return
    message = (f"\n\r{{GGrapevine {{B{channel}{{x Chat{{x:{{y{name.capitalize()}"
               f"@{game.capitalize()}{{x:{{G{message}{{x")

    if message != "":
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for eachplayer in grape_enabled:
            if channel in eachplayer.oocflags['grapevine_channels']:
                eachplayer.write(message)


async def cmd_grapevine_player_login(message):
    msg = f"\n\r{{GGrapevine Status Update: {message}{{x"

    grape_enabled = [players for players in player.playerlist
                     if players.oocflags_stored['grapevine'] == 'true']
    for eachplayer in grape_enabled:
        eachplayer.write(msg)


async def cmd_grapevine_player_logout(message):
    msg = f"\n\r{{GGrapevine Status Update: {message}{{x"

    grape_enabled = [players for players in player.playerlist
                     if players.oocflags_stored['grapevine'] == 'true']
    for eachplayer in grape_enabled:
        eachplayer.write(msg)


async def handle_grapevine_messages() -> None:
    commands = {'tells/send': cmd_grapevine_tells_send,
                'tells/receive': cmd_grapevine_tells_receive,
                'games/connect': cmd_grapevine_games_connect,
                'games/disconnect': cmd_grapevine_games_disconnect,
                'channels/broadcast': cmd_grapevine_channels_broadcast,
                'player/login': cmd_grapevine_player_login,
                'player/logout': cmd_grapevine_player_logout}

    while status.grapevine['connected']:
        message = await grapevine.messages_to_game.get()

        event_type, values = message
        if event_type in commands:
            commands[event_type](values)


async def handle_events() -> None:
    while status.server['running']:
        await asyncio.sleep(0.0625)
        event.heartbeat()

if __name__ == '__main__':
    log.info('Starting Dark Waters')

    parser = argparse.ArgumentParser(
        description='Change the option prefix characters',
        prefix_chars='-+/',
    )

    parser.add_argument('-d', action='store_true',
                        default=None,
                        help='Set log level to debug',
                        )

    args = parser.parse_args()

    logging.basicConfig(filename=serverlog, filemode='w',
                        format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG if args.d else logging.INFO)
    log: logging.Logger = logging.getLogger(__name__)

    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig, loop)))

    loop.set_exception_handler(handle_exception_generic)

    helpsys.init()
    races.init()
    area.init()

    engine_tasks = [frontend.connect(),
                    grapevine.connect(),
                    handle_commands(),
                    handle_messages(),
                    handle_grapevine_messages(),
                    handle_events()]

    asyncio.gather(*engine_tasks, return_exceptions=True)

    loop.run_forever()

    player_quit = 'quit force'

    if status.server['softboot']:
        log.info('Softboot has been executed')
        asyncio.gather(frontend.msg_gen_game_softboot(wait_time=1), return_exceptions=True)
        player_quit = 'quit force no_notify'

    # server.Server.done has been set to True
    for each_player in sessions.values():
        each_player.owner.interp(player_quit)
        each_player.handle_close()

    log.info('Dark Waters shutdown.')
    loop.close()
