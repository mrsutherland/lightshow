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
