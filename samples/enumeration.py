import time
from led import Color, LED
import xbee_leds


if __name__ == '__main__':
    xbees = xbee_leds.get_xbee_list(True)
    if not xbees:
        raise Exception('No XBees found on network') 
    eui = xbees[0]
    
    #initialize ZigBee driver
    xbee_leds.initialize()

    while True:
        for c in (Color(red=0xF), Color(blue=0xF), Color(green=0xf), Color(0xf, 0xf, 0xf)):
            for i in xrange(50):
                bulb = LED(i, c)
                time.sleep(.25)
                xbee_leds.send_leds(bulb.export(), eui)
        
        # make sure we don't try to send too fast
        while xbee_leds.queue_size(eui) > 3:
            time.sleep(0.01)
