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
