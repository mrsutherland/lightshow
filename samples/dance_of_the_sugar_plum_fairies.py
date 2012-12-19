import time
from led import Color, CompactLEDs
import xbee_leds
import mp3play

DATA_FILE = r'Dance of the Sugar Plum Fairy - Sheet1.csv'
MUSIC_FILE = r'dance of the sugar plum fairy.mp3' # http://www.thelogoedcd.com/section_pics/dotspf.mp3

def set_leds(strand, scale, thrum, bell, warble):
    #thrum is bottom of tree
    if thrum == 1:
        for i in xrange(16):
            strand[i] = Color(red=0xF)
    elif thrum == 2:
        for i in xrange(16):
            strand[i] = Color(red=0xF, blue=0xF)
    if thrum:
        #scale colors
        for color in strand[:16]:
            color.red = int(color.red * scale)
            color.blue = int(color.blue * scale)
            color.green = int(color.green * scale)
    #bell is top of tree
    if bell == 1:
        for i in xrange(16, len(strand)):
            strand[i] = Color(green=0xF)
    elif bell == 2:
        for i in xrange(16, len(strand)):
            strand[i] = Color(green=0xF, blue=0xF)
    elif bell == 3:
        for i in xrange(16, len(strand)):
            strand[i] = Color(blue=0xF)
    elif bell == 4:
        for i in xrange(16, len(strand)):
            strand[i] = Color(red=0xF, blue=0xF, green=0xF)
    if bell:
        #scale colors
        for color in strand[16:]:
            color.red = int(color.red * scale)
            color.blue = int(color.blue * scale)
            color.green = int(color.green * scale)
    # warble is whole tree
    if warble == 1:
        for i in xrange(len(strand)):
            strand[i] = Color(red=0xF)
    elif warble == 2:
        for i in xrange(len(strand)):
            strand[i] = Color(red=0xF, blue=0xF)
    if warble == 3:
        for i in xrange(len(strand)):
            strand[i] = Color(blue=0xF)
    elif warble == 4:
        for i in xrange(len(strand)):
            strand[i] = Color(green=0xF)
    if warble:
        #scale colors
        for color in strand:
            color.red = int(color.red * scale)
            color.blue = int(color.blue * scale)
            color.green = int(color.green * scale)
                 

times = []
with open(DATA_FILE, 'r') as data_file:
    for line in data_file:
        try:
            values = line.split(',')
            start = float(values[0].strip())
            if values[1]:
                stop = float(values[1].strip())
            else:
                stop = start + 0.1
            scale = float(values[2].strip() or '1.0')
            thrum = int(values[3].strip() or '0')
            bell = int(values[4].strip() or '0')
            warble = int(values[5].strip() or '0')
            if start and stop:
                times.append((start, stop, scale, thrum, bell, warble))
        except:
            pass #ignore headers, blank lines, and others

strand = CompactLEDs()

xbees = xbee_leds.get_xbee_list(True)
if not xbees:
    raise Exception('No XBees found on network') 
eui = xbees[0]

xbee_leds.initialize()

clip = mp3play.load(MUSIC_FILE)
clip.play()
start_time = time.time()
for start, stop, scale, thrum, bell, warble in times:
    while time.time() < start_time + start:
        time.sleep(.001)
    set_leds(strand, scale, thrum, bell, warble)
    xbee_leds.send_compact_leds(strand.export(), eui)
xbee_leds.send_compact_leds(CompactLEDs().export(), eui) #turn off lights at end.
clip.stop()
