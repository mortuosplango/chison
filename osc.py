# osc
import inspect
import os
import sys

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"pyosc")))
if cmd_subfolder not in sys.path:
     sys.path.insert(0, cmd_subfolder)

from OSC import OSCClient, OSCMessage

def set_port(port=57120):
     global client
     client.connect( ("localhost", port) )


def send_osc(addr, *args):
        msg = OSCMessage(addr)
        for d in args:
            msg.append(d)
        return client.send(msg)


client = OSCClient()
set_port(57120)

from OSC import OSCServer
import sys
from time import sleep
import threading

server = OSCServer( ("localhost", 7110) )
server.timeout = 0
run = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
server.handle_timeout = types.MethodType(handle_timeout, server)

def server_loop():
     while run:
         server.timed_out = False
         # handle all pending requests then return
         while not server.timed_out:
             server.handle_request()
         sleep(1)
     server.close()

server_thread = threading.Thread(target=server_loop)
server_thread.start()
