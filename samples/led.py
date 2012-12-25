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

import struct

class Color:
    def __init__(self, red=0, green=0, blue=0, brightness=0xff):
        self.red = red
        self.green = green
        self.blue = blue
        self.brightness = brightness

    def __mul__(self, b):
        return Color(self.red*b, self.green*b, self.blue*b, self.brightness)
    __rmul__ = __mul__
    
    def __div__(self, b):
        return self.__mul__(1.0/b)
    
    def __add__(self, b):
        #do not add brightness
        return Color(self.red+b.red, self.green+b.green, self.blue+b.blue, self.brightness)
    
    def __sub__(self, b):
        #do not subtract brightness...
        return Color(self.red-b.red, self.green-b.green, self.blue-b.blue, self.brightness)
    
    def scale(self, scalar):
        #scale the color, this is useful for gradients and fading
        self.red *= scalar
        self.green *= scalar
        self.blue *= scalar


class LED:
    def __init__(self, number, color=None):
        self.number = number
        self.color = color or Color()
        
    def export(self):
        return struct.pack('<BBBB', self.number, 
                            int(self.color.brightness), 
                            ((int(self.color.blue) & 0xF) << 4) + (int(self.color.green) & 0xF), 
                            ((int(self.color.red) & 0xF) << 4))

class CompactLEDs(list):
    def __init__(self, color=None):
        list.__init__(self)
        for _ in xrange(50):
            self.append(color or Color())

    def export(self):
        out_str = ''
        for i in xrange(0, 50, 2):
            out_str += struct.pack('<BBB',
                                   ((int(self[i].blue) & 0xF) << 4) + (int(self[i].green) & 0xF),
                                   ((int(self[i].red) & 0xF) << 4) + (int(self[i+1].blue) & 0xF),
                                   ((int(self[i+1].green) & 0xF) << 4) + (int(self[i+1].red) & 0xF))
        return out_str

    def gradient(self, start_led, start_color, end_led, end_color):
        if end_led < start_led:
            #roll around array
            end_led += len(self)
        num_leds = end_led - start_led
        for led_num in xrange(num_leds):
            self[(start_led+led_num)%len(self)] = (start_color * (num_leds-led_num) + end_color * (led_num)) / num_leds
        
    def gradients(self, points): #points is a list of tuple(led_num, color)
        prev_num, prev_color = points[0]
        for led_num, color in points[1:]:
            self.gradient(prev_num, prev_color, led_num, color)
            prev_num = led_num
            prev_color = color
