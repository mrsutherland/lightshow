import time
from led import Color, CompactLEDs
import xbee_leds


if __name__ == '__main__':
    xbees = xbee_leds.get_xbee_list(True)
    if not xbees:
        raise Exception('No XBees found on network') 
    eui = xbees[0]
    
    #initialize ZigBee driver
    xbee_leds.initialize()

    # create gradient
    leds = CompactLEDs()
    leds.gradients([(0, Color(red=0xF)), 
                    (17, Color(green=0xF)),
                    (34, Color(blue=0xF)),
                    (0, Color(red=0xF))
                    ])
    while True:
        # shift all of the leds by one
        color = leds.pop()
        leds.insert(0, color)
        # send led colors
        xbee_leds.send_compact_leds(leds.export(), eui)
        
        # make sure we don't try to send too fast
        while xbee_leds.queue_size(eui) > 3:
            time.sleep(0.01)
