import zigbee #@UnusedImport
import socket
import struct
import time
import select
import random
from threading import Thread, RLock

class ZigBee_LED(Thread):
    SIMULTANEOUS_MSGS = 3
    #NOTE: this class relies on the socket to always give back a tx_status for a send.
    
    def __init__(self):
        Thread.__init__(self)
        # create ZigBee socket
        self.sock = socket.socket(socket.AF_XBEE, socket.SOCK_DGRAM, socket.XBS_PROT_TRANSPORT) #@UndefinedVariable
        self.sock.bind(('', 0x15, 0, 0))
        self.sock.setblocking(0) # set nonblocking
        self.sock.setsockopt(socket.XBS_SOL_EP, socket.XBS_SO_EP_TX_STATUS, 1) # enable transmission status messages @UndefinedVariable
        # socketpair for interrupting selects
        self.wake_sock_send, self.wake_sock_recv = socket.socketpair() #@UndefinedVariable
        # internal vars
        self.outgoing = {} # messages waiting to send {eui: (data, addr)}
        self.in_the_air = {} # how messages in the air right now {eui: count}
        self.active_ids = {} # active tx_ids mapping back to euis {tx_id: eui}
        self.tx_id = 0
        self.lock = RLock()
    
    def run(self):
        while True:
            # send messages
            with self.lock:
                for eui, message_tuples in self.outgoing.iteritems():
                    while len(message_tuples) and self.in_the_air[eui] < self.SIMULTANEOUS_MSGS:
                        # can send another message
                        payload, addr = message_tuples.pop(0)
                        tx_id = self.next_tx_id()
                        addr += (0, tx_id) #add options and tx_id fields
                        self.active_ids[tx_id] = eui
                        self.in_the_air[eui] += 1
                        self.sock.sendto(payload, addr)
            # recv messages
            rlist = select.select([self.sock, self.wake_sock_recv], [], [])[0]
            if self.wake_sock_recv in rlist:
                self.wake_sock_recv.recvfrom(255) #clear socket
            if self.sock in rlist:
                data, addr = self.sock.recvfrom(255) #@UnusedVariable
                #only expecting tx status messages
                if len(addr) < 6:
                    continue
                tx_id = addr[5]
                with self.lock:
                    eui = self.active_ids.pop(tx_id)
                    self.in_the_air[eui] -= 1
        
    def next_tx_id(self):
        with self.lock:
            self.tx_id += 1
            if self.tx_id > 0xFF:
                self.tx_id = 1
            return self.tx_id
    
    def send_leds(self, payload, eui):
        self.add_to_queue(payload, eui, 0x11ed)
    
    def send_compressed_leds(self, payload, eui):
        self.add_to_queue(payload, eui, 0xc1ed)
            
    def add_to_queue(self, payload, eui, cluster):
        with self.lock:
            # add message to outgoing queue
            eui = eui.lower()
            if eui not in self.outgoing:
                self.outgoing[eui] = []
                self.in_the_air[eui] = 0
            addr = (eui, 0x15, 0x1ed5, cluster)
            self.outgoing[eui].append((payload, addr))
            # wake up send thread
            self.wake_sock_send.send(chr(42))
    
    def queue_size(self, eui):
        return len(self.outgoing.get(eui, []))

# Create ZigBee object and register functions
zigbee_led = None
send_leds = None
send_compressed_leds = None
queue_size = None

def initialize():
    global zigbee_led
    global send_leds
    global send_compressed_leds
    global queue_size    
    if not zigbee_led:
        zigbee_led = ZigBee_LED()
        zigbee_led.start()
        
        send_leds = zigbee_led.send_leds
        send_compressed_leds = zigbee_led.send_compressed_leds
        queue_size = zigbee_led.queue_size
