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

import led
import xbee_leds
import random

class Twinkle:
    active = set()
    STEPS = 16.0
    def __init__(self, color):
        self.led = None
        self.target_color = color
        self.step = 0
        self.offset = 1
        
    def init_led(self):
        number = random.randint(0, 500)
        if number < 50 and number not in self.active:
            self.active.add(number)
            self.led = led.LED(number, led.Color(brightness=0xFF))
            self.step = 0
            self.offset = 1
    
    def calc_color(self):
        scalar = float(self.step) / self.STEPS
        return self.target_color * scalar
    
    def tick(self):
        response = ''
        if self.led is not None:
            self.step += self.offset
            self.led.color = self.calc_color()
            response = self.led.export()
            if self.step >= self.STEPS:
                self.offset = -1
            if self.step <= 0:
                self.active.remove(self.led.number)
                self.led = None
        else:
            self.init_led()
        return response

if __name__ == '__main__':
    import time
    
    xbees = xbee_leds.get_xbee_list(True)
    if not xbees:
        raise Exception('No XBees found on network') 
    eui = xbees[0]
    #initialize XBee
    xbee_leds.initialize()
    
    #turn off any leftover color
    compact = led.CompactLEDs()
    xbee_leds.send_compact_leds(compact.export(), eui)
    
    leds = []
    twinkles = []
    colors = [led.Color(red=0x0F), #red
              led.Color(green=0x0F), #green
              led.Color(blue=0x0F), #blue
              led.Color(red=0xF, blue=0x0F), #purple
              led.Color(green=0x0F, blue=0xF), #teal
              led.Color(red=0x0F, green=0x8), #yellow/orange
              led.Color(red=0x0E, green=0xE, blue=0xE) #white
              ]
    for color in colors:
        for _ in xrange(5):
            twinkles.append(Twinkle(color))
    while True:
        for twinkle in twinkles:
            response = twinkle.tick()
            if response:
                leds.append(response)
        if leds:
            for i in xrange(0, len(leds), 20):
                # only send up to 20 leds at a time
                xbee_leds.send_leds(''.join(leds[i:i+20]), eui.lower())
            leds = []
        # make sure we don't try to send too fast
        while xbee_leds.queue_size(eui) > 3:
            time.sleep(0.01)
