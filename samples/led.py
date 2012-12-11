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

class LED:
    def __init__(self, number, color):
        self.number = number
        self.color = color
        
    def export(self):
        return struct.pack('<BBBB', self.number, 
                            self.color.brightness, 
                            ((self.color.blue & 0xF) << 4) + (self.color.green & 0xF), 
                            ((self.color.red & 0xF) << 4))

class CompactLEDs(list):
    def __init__(self):
        list.__init__(self)
        for _ in xrange(50):
            self.append(Color())

    def export(self):
        out_str = ''
        for i in xrange(0, 50, 2):
            out_str += struct.pack('<BBB',
                                   ((self[i].blue & 0xF) << 4) + (self[i].green & 0xF),
                                   ((self[i].red & 0xF) << 4) + (self[i+1].blue & 0xF),
                                   ((self[i+1].green & 0xF) << 4) + (self[i+1].red & 0xF))
        return out_str
