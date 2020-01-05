#! usr/bin/env python
# Project: Akrios
# Filename: server.py
# 
# File Description: The main server module.
# 
# By: Jubelo

import logging
import string
import time
import sys

import grapevine
import helpsys
import color
import area
import comm
import frontend
import login
import races
import event

log = logging.getLogger(__name__)

# This is outside the scope of the rest of this module so we have a good
# reference time to base our total startup time.  Used only in the server
# __init__ to determine startup time.
startup = time.time()

# This is the dict of connected sessions.
session_list = {}

# Assistant variables for removing certain characters from our input.
validchars = string.printable
validchars = validchars.replace(string.whitespace[1:], "")


class Session(object):
    def __init__(self, uuid_, addr_, port_):
        self.owner = None
        self.host = addr_
        self.port = port_
        self.session = uuid_
        self.ansi = True
        self.promptable = False
        self.inbuf = []
        self.outbuf = ''
        self.state = {'connected': True,
                      'logged in': False}
        self.events = event.Queue(self, "session")

        self._login()

    def clear(self):
        del self

    def handle_close(self):
        self.state['connected'] = False
        self.state['logged in'] = False
        del self

    def do_echo_telnet(self):
        pass

    def dont_echo_telnet(self):
        pass

    def _login(self):
        newconn = login.Login()
        newconn.sock = self
        newconn.sock.owner = newconn
        session_list[self.session] = self
        newconn.greeting()
        comm.wiznet(f"Accepting connection from: {newconn.sock.host}")

    def dispatch(self, msg, trail=True):
        if trail:
            msg = f"{msg}\n\r"
        if self.ansi:
            msg = color.colorize(msg)
        else:
            msg = color.decolorize(msg)
        self.outbuf = f"{self.outbuf}{msg}"

        if hasattr(self.owner, "snooped_by") and len(self.owner.snooped_by) > 0:
            for each_person in self.owner.snooped_by:
                each_person.write(self.outbuf)

    def send(self, msg_):
        log.debug(f'Sending {msg_} to {self.session}')
        frontend.fesocket.msg_gen_player_output(msg_, self.session)

    @property
    def writable(self):
        return True if self.outbuf else False

    def write(self):
        try:
            self.send(self.outbuf)
            self.outbuf = ""
            if hasattr(self.owner, "editing"):
                output = ">"
                self.send(output)
            elif self.promptable:
                if self.owner.oocflags["afk"]:
                    pretext = "{W[{RAFK{W]{x "
                else:
                    pretext = ""
                output = color.colorize(f"\n\r{pretext}{self.owner.prompt}\n\r")
                self.send(output)
        except Exception as err:
            log.error(f"handle_write : {err}")

    @property
    def readable(self):
        return True if self.inbuf else False

    def read(self):
        self.owner.interp(self.inbuf.pop(0))


class Server(object):
    done = False
    softboot = False
    
    def __init__(self):
        super().__init__()
        log.info("Starting Akrios main loop.")
        self.events = event.Queue(self, "server")

        helpsys.init()
        races.init()
        area.init()

        event.init_events_server(self)

        if grapevine.LIVE:
            log.info("grapevine.LIVE : Creating Grapevine Socket.")
            grapevine.gsocket = grapevine.GrapevineSocket()

            grapevine_connected = grapevine.gsocket.gsocket_connect()
            if not grapevine_connected:
                log.warning("Could not connect to grapevine on startup.")

        log.info("Creating Front End Socket")
        frontend.fesocket = frontend.FESocket()
        frontend_connected = frontend.fesocket.fesocket_connect()
        if not frontend_connected:
            log.warning("Could not connect to front end on startup.")

        log.info(f"Akrios is up and running in {time.time() - startup:,.6f} seconds.")

    @staticmethod
    def run():
        currenttime = time.time
        while not Server.done:
            timedelta = currenttime() + 0.0625

            event.heartbeat()

            for each_session, session_obj in session_list.items():
                if session_obj.state['connected']:
                    if session_obj.writable:
                        session_obj.write()
                    if session_obj.readable:
                        session_obj.read()

            [session.handle_close() for session in session_list.values() if not session.state['connected']]

            timenow = currenttime()
            if timenow < timedelta:
                time.sleep(timedelta - timenow)
        if not Server.softboot:
            # XXX Save all players before hard close! XXX
            [session.handle_close() for session in session_list.values()]
        else:
            # Add in a "copyover" style soft reboot.
            # Save state, save players, save file descriptors to disk.
            # Restart Mud, reload file descriptors and load players.
            # XXX Implement this at some point.
            pass
        log.info("System shutdown successful.")
        sys.exit()
