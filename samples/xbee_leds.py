# Copyright (c) 2012 Michael Sutherland, Null Squared LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

from cp4pc import zigbee #@UnusedImport - needed to modify socket on PC to support XBee sockets
import socket
import select
import time
from threading import Thread, RLock

TIMEOUT=5 #5 second message timeout

def get_xbee_list(refresh=False):
    #return list of discovered EUIs on the network (skip first node which is self)
    return [node.addr_extended.lower() for node in zigbee.get_node_list(refresh)][1:]

class XBee_LED(Thread):
    SIMULTANEOUS_MSGS = 3
    ENDPOINT_ID = 0xE8
    PROFILE_ID = 0xC105
    LED_CLUSTER = 0x0011
    LED_CLUSTER_COMPACT = 0xC1ED
    #NOTE: this class relies on the socket to always give back a tx_status for a send.
    
    def __init__(self):
        Thread.__init__(self)
        # create ZigBee socket
        self.sock = socket.socket(socket.AF_XBEE, socket.SOCK_DGRAM, socket.XBS_PROT_TRANSPORT) #@UndefinedVariable
        self.sock.bind(('', self.ENDPOINT_ID, 0, 0))
        self.sock.setblocking(0) # set nonblocking
        self.sock.setsockopt(socket.XBS_SOL_EP, socket.XBS_SO_EP_TX_STATUS, 1) # enable transmission status messages @UndefinedVariable
        # socketpair for interrupting selects
        self.wake_sock_send, self.wake_sock_recv = socket.socketpair() #@UndefinedVariable
        # internal vars
        self.outgoing = {} # messages waiting to send {eui: (data, addr)}
        self.in_the_air = {} # how messages in the air right now {eui: count}
        self.active_ids = {} # active tx_ids mapping back to euis {tx_id: (eui, timestamp)}
        self.tx_id = 0
        self.lock = RLock()
        self.quit = False
    
    def run(self):
        while not self.quit:
            #check for message timeouts
            with self.lock:
                for tx_id, (eui, timestamp) in self.active_ids.items():
                    if time.time() > timestamp + TIMEOUT:
                        # message timed out, remove from queue and keep sending
                        print "ERROR: timeout eui=%s, tx_id=%d, time=%s" % (eui, tx_id, time.ctime())
                        del self.active_ids[tx_id]
                        self.in_the_air[eui] -= 1
            
            # send messages
            with self.lock:
                for eui, message_tuples in self.outgoing.iteritems():
                    while len(message_tuples) and self.in_the_air[eui] < self.SIMULTANEOUS_MSGS:
                        # can send another message
                        payload, addr = message_tuples.pop(0)
                        tx_id = self.next_tx_id()
                        addr += (0, tx_id) #add options and tx_id fields
                        self.active_ids[tx_id] = (eui, time.time())
                        self.in_the_air[eui] += 1
                        self.sock.sendto(payload, addr)
            # recv messages
            rlist = select.select([self.sock, self.wake_sock_recv], [], [], 0.1)[0]
            if self.wake_sock_recv in rlist:
                self.wake_sock_recv.recvfrom(255) #clear socket
            if self.sock in rlist:
                data, addr = self.sock.recvfrom(255) #@UnusedVariable
                #only expecting tx status messages
                if len(addr) < 6:
                    continue
                #extract tx_id and make room for another message to send
                tx_id = addr[5]
                with self.lock:
                    if tx_id in self.active_ids:
                        eui = self.active_ids.pop(tx_id)[0]
                        self.in_the_air[eui] -= 1
        
    def next_tx_id(self):
        with self.lock:
            self.tx_id += 1
            if self.tx_id > 0xFF:
                self.tx_id = 1
            return self.tx_id
    
    def send_leds(self, payload, eui):
        self.add_to_queue(payload, eui, self.LED_CLUSTER)
    
    def send_compact_leds(self, payload, eui):
        self.add_to_queue(payload, eui, self.LED_CLUSTER_COMPACT)
            
    def add_to_queue(self, payload, eui, cluster):
        with self.lock:
            # add message to outgoing queue
            eui = eui.lower()
            if eui not in self.outgoing:
                self.outgoing[eui] = []
                self.in_the_air[eui] = 0
            addr = (eui, self.ENDPOINT_ID, self.PROFILE_ID, cluster)
            self.outgoing[eui].append((payload, addr))
            # wake up send thread
            self.wake_sock_send.send(chr(42))
    
    def queue_size(self, eui):
        return len(self.outgoing.get(eui, []))

    def close(self):
        self.quit = True

# Create XBee object and register functions
xbee_led = None
send_leds = None
send_compact_leds = None
queue_size = None

def initialize():
    global xbee_led
    global send_leds
    global send_compact_leds
    global queue_size    
    if not xbee_led:
        xbee_led = XBee_LED()
        xbee_led.start()
        
        send_leds = xbee_led.send_leds
        send_compact_leds = xbee_led.send_compact_leds
        queue_size = xbee_led.queue_size

def close():
    xbee_led.close()
