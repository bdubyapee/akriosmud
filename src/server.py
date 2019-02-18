#! usr/bin/env python
# Project: Akrios
# Filename: server.py
# 
# File Description: The main server module.
# 
# By: Jubelo

import asyncore
import os
from socket import AF_INET, AF_INET6, SOCK_STREAM
import string
from telnetlib import IAC, DONT, DO, WONT, WILL, theNULL, ECHO, SGA
import time
import sys

import grapevine
import helpsys
import color
import area
import comm
import login
import races
import event
import world


# Temp for testing
import mobile
import objects

# This is outside the scope of the rest of this module so we have a good
# reference time to base our total startup time.  Used only in the server
# __init__ to determine startup time.
startup = time.time()

# This is the list of connected socket objects.
connlist = []

# Assistant variables for removing certain characters from our input.
validchars = string.printable
validchars = validchars.replace(string.whitespace[1:], "")

# Variables containing telnet codes for Go-Ahead Suppression
SGARequest = IAC + WILL + SGA
SGAAcknowledge = IAC + DO + SGA
DOECHOTELNET = IAC + WONT + ECHO + theNULL
DONTECHOTELNET = IAC + WILL + ECHO + theNULL

class ConnSocket(asyncore.dispatcher):

    def __init__(self, connection, address):
        super().__init__(connection) 
        self.owner = None
        self.host = address[0]
        self.inbuf = ""
        self.outbuf = ""
        self.ansi = True
        self.promptable = False
        self.suppressgoahead = False
        self.events = event.Queue(self, "socket")
        event.init_events_socket(self)

    def clear(self):
        self.owner = None
        self.host = None
        self.inbuf = ""
        self.outbuf = ""
        self.ansi = True
        self.promptable = False
        self.suppressgoahead = False
        self.events = None

    def do_echo_telnet(self):
        try:
            self.send(DOECHOTELNET)
        except:
            pass
        return

    def dont_echo_telnet(self):
        try:
            self.send(DONTECHOTELNET)
        except:
            pass
        return        
        
    def writable(self):
        if self.outbuf != "":
            return True
        return False

    def parse_input(self, text):
        # Below we decode the bytes input into a string,
        # linux telnet sends a 255 line after each input.
        # We check for that below.  Kinda ugly, but not sure how to handle it otherwise.
        if text.startswith(b"\xff"):
            return ''
        try:
            text = text.decode("utf8")
        except Exception as err:
            to_log = (f"Error parsing input:\n\r",
                      f"Host: {self.host}\n\r",
                      f"Error: {err}\n\r")
            comm.log(world.serverlog, f"{to_log}")
            return
        # Here we check if there has just been an enter pressed.
        if text == "\r\n":
            return text
    
        # Sift through the input and validate good alphanums using a comprehension.
        output = "".join(char for char in text if char in validchars)
        
        output = output.lstrip()

        if len(output) > 0:
            output = f"{output}\r\n"
        else:
            output = ""

        return output

    def handle_read(self):
        try:
            indata = self.recv(4096)
        except Exception as err:
            self.handle_close()
            comm.log(world.serverlog, f"Error in handle_read:server.py : {err}")
     

        # Clients usually send the Suppress-Go-Ahead on connection.  This
        # tests for the suggestion, and sends the "Go ahead and suppress it"
        # code.
        if indata == SGARequest:
            indata = ""
            if not self.suppressgoahead:
                self.send(SGAAcknowledge)
                self.suppressgoahead = True

        self.inbuf = f"{self.inbuf}{self.parse_input(indata)}"
        
        if '\r\n' in self.inbuf:
            args, self.inbuf = self.inbuf.split('\r\n')
            self.owner.interp(args)

    def handle_write(self):
        try:
            self.send(self.outbuf.encode("utf8"))
            self.outbuf = ""
            if hasattr(self.owner, "editing"):
                output = ">"
                self.send(output.encode("utf8"))
            elif self.promptable == True:
                if self.owner.oocflags["afk"] == True:
                    pretext = "{W[{RAFK{W]{x "
                else:
                    pretext = ""
                    
                output = color.colorize(f"\n\r{pretext}{self.owner.prompt}")
                self.send(output.encode("utf8"))
        except Exception as err:
            self.handle_close()
            comm.log(world.serverlog, f"Error in handle_write:server.py - {err}")

    def handle_close(self):
        if self in connlist:
            connlist.remove(self)
        self.clear()
        self.close()
        del(self)

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


class Server(asyncore.dispatcher):
    done = False
    softboot = False
    
    def __init__(self):
        super().__init__()
        self.logpath = os.path.join(world.logDir, "server")
        self.events = event.Queue(self, "server")      
        self.create_socket(AF_INET6, SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", 4000))
        self.listen(5)
        
        
        helpsys.init()
        races.init()
        area.init()


        # Temp for testing XXX
        if 1001 in mobile.mobilelist_by_vnum_index:
            mobile.mobilelist_by_vnum_index[1001].create_real(location=1001)
        if 1001 in objects.objectlist_by_vnum_index:
            objects.objectlist_by_vnum_index[1001].create_real(location=1001)

        event.init_events_server(self)

        grapevine.gsocket = grapevine.GrapevineSocket()

        grapevine_connected = grapevine.gsocket.gsocket_connect()
        if grapevine_connected == False:
            print("Could not connect to grapevine on startup.")

        print(f"Akrios is up and running in {time.time() - startup:,.6f} seconds.")

    def run(self):
        currenttime = time.time
        while not Server.done:
            timedelta = currenttime() + 0.125
            asyncore.poll()
            event.heartbeat()
            timenow = currenttime()
            if timenow < timedelta:
                time.sleep(timedelta - timenow)
        if Server.softboot == False:
            for conn in connlist:
                conn.close()
        else:
            # Add in a "copyover" style soft reboot.
            # Save state, save players, save file descriptors to disk.
            # Restart Mud, reload file descriptors and load players.
            # XXX Implement this at some point.
            pass
        print("System shutdown successful.")
        sys.exit()

    def handle_accept(self):
        newconn = login.Login()
        connection, address = self.accept()
        sock = ConnSocket(connection, address)
        newconn.sock = sock
        newconn.sock.owner = newconn
        connlist.append(sock)
        newconn.greeting()
        comm.wiznet(f"Accepting connection from: {newconn.sock.host}")
        return sock

