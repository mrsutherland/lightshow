/***** XBEE APPLICATION PROJECT *****
 * 
 * Auto-generated header with information about the 
 * relation between the XBee module pins and the 
 * project components.
 * 
 ************ XBEE LAYOUT ***********
 * 
 * This layout represents the XBee S2B module selected 
 * for the project with its pin distribution:
 *               _________________
 *              /     ________    \ 
 *             /     |   __   |    \ 
 *            /      | //  \\ |     \ 
 *   XPIN1  -|       | \\__// |      |- XPIN20
 *   XPIN2  -|       |________|      |- XPIN19
 *   XPIN3  -|                       |- XPIN18
 *   XPIN4  -| ===================== |- XPIN17
 *   XPIN5  -| #   # ####  #### #### |- XPIN16
 *   XPIN6  -|  # #  #   # #    #    |- XPIN15
 *   XPIN7  -|   #   ####  ###  ###  |- XPIN14
 *   XPIN8  -|  # #  #   # #    #    |- XPIN13
 *   XPIN9  -| #   # ####  #### #### |- XPIN12
 *   XPIN10 -| ===================== |- XPIN11
 *           |_______________________|
 * 
 ************ PINS LEGEND ***********
 * 
 * The following list displays all the XBee Module pins 
 * with the project component which is using each one:
 * 
 *   XPIN1 = VCC
 *   XPIN2 = <<UNUSED>>
 *   XPIN3 = <<UNUSED>>
 *   XPIN4 = spi0 [MISO Pin]
 *   XPIN5 = special0 [Reset Pin]
 *   XPIN6 = <<UNUSED>>
 *   XPIN7 = <<UNUSED>>
 *   XPIN8 = <<UNUSED>>
 *   XPIN9 = <<UNUSED>>
 *   XPIN10 = GND
 *   XPIN11 = spi0 [MOSI Pin]
 *   XPIN12 = <<UNUSED>>
 *   XPIN13 = <<UNUSED>>
 *   XPIN14 = <<UNUSED>>
 *   XPIN15 = special0 [Association Pin]
 *   XPIN16 = <<UNUSED>>
 *   XPIN17 = <<UNUSED>>
 *   XPIN18 = spi0 [SPSCK Pin]
 *   XPIN19 = <<UNUSED>>
 *   XPIN20 = special0 [Commissioning Pin]
 *
 ************************************/

#include <xbee_config.h>
#include <types.h>

#define DELAY_us 30

// timer settings for different bits
#define TIMER_0 240
#define TIMER_1 480
#define TIMER_END 720  // modulo number
#define TIMER_OFF TIMER_END+1

void _delay_10_us(void) {
	uint8_t i;
	for(i=0; i<DELAY_us; ++i);
}

// struct mirrors the data being sent over the line to set an LED
// number only uses last 6 bits - 0x3F is a special broadcast address
// extra bits aren't being used right now.
// NOTE: as far as I can tell, halving the brightness is the same as
// halving all of the color values.  Think of the brightness as a scalar.
struct LED {
	uint8_t number;
	uint8_t brightness;
	uint8_t green:4;
	uint8_t blue:4;
	uint8_t extra:4;
	uint8_t red:4;
};

// Variables for timer interrupt
struct LED *cur_led;
uint8_t led_cur_byte;
uint8_t led_bit_mask;
uint16_t led_next_bit = TIMER_OFF;

//interrupt 9 void Vtpm2ch1_isr(void)
#pragma TRAP_PROC
interrupt void Vtpm2ovf_isr(void)
{
	// Interrupt to send data to LEDs
	// I'm using a PWM to send individual bits.
	// The PWM period is fixed, I modify the duty cycle for each bit.
	//                              _                       __
	// A "1" is sent as (001) or __|  and "0" is (011) or _|
	// TIMER_0 and TIMER_1 are set to send a "0" or "1" bit.
	// TIMER_END and TIMER_OFF are set so that the line is kept low the whole time.
	// Because this is a very quick interrupt, I set the next bit at the beginning
	// of the interrupt and then calculate what the next bit is going to be.
	
	// reset interrupt
	TPM2SC_TOF = 0;

	// set the next bit
	TPM2C0V = led_next_bit;
	
	if (led_next_bit < TIMER_END) {
		// calculate the next bit
		if (((uint8_t*) cur_led)[led_cur_byte] & led_bit_mask) {
			// next bit is 1
			led_next_bit = TIMER_1;
		} else {
			// next bit is 0
			led_next_bit = TIMER_0;
		}
		// move the counters to the next bit
		led_bit_mask >>= 1;
		if (!led_bit_mask) {
			// roll over to the next byte
			led_bit_mask = 0x80;
			++led_cur_byte;
		} else if (led_bit_mask == 0x04 && led_cur_byte == 3) {
			// this is the end of the led, switch to END mode
			led_next_bit = TIMER_END;
		}
	} else if (led_next_bit == TIMER_END) {
		// Have to keep the line low between LEDs for a bit count.
		led_next_bit = TIMER_OFF;
	}
}

void send_led(struct LED* next_led) 
{
	// Sets up interrupt to set 1 LED
	// First wait until we are done sending current LED
	// Then reset LED pointer, masks, and state.
	while(led_next_bit != TIMER_OFF);
	cur_led = next_led;
	led_cur_byte = 0;
	led_bit_mask = 0x20; // skip first two bits 
	led_next_bit = TIMER_1;
}

#if defined(ENABLE_XBEE_HANDLE_RX_EXPLICIT_FRAMES) || \
    defined(ENABLE_XBEE_HANDLE_RX_ZCL_FRAMES) || \
    defined(ENABLE_XBEE_HANDLE_ND_RESPONSE_FRAMES)

#include "zigbee/zdo.h"

int led_handler(const wpan_envelope_t FAR *envelope, void FAR *context)
{
	// Accepts incoming LED data.
	uint8_t i;
	for (i = 0; i < envelope->length >> 2; i++) {
		send_led((struct LED*)envelope->payload + i);
	}
	while(led_next_bit != TIMER_OFF); // wait for leds to finish being sent
	return 0;
}

const wpan_cluster_table_entry_t light_show_clusters[] = {
	{0x11ed, led_handler, NULL,	WPAN_CLUST_FLAG_INPUT | WPAN_CLUST_FLAG_NOT_ZCL},
    WPAN_CLUST_ENTRY_LIST_END
};

/* Used to track ZDO transactions in order to match responses to requests
   (#ZDO_MATCH_DESC_RESP). */
wpan_ep_state_t zdo_ep_state = { 0 };

const wpan_endpoint_table_entry_t endpoints_table[] = {
    /* Add your endpoints here */

    ZDO_ENDPOINT(zdo_ep_state),

    /* Digi endpoints */
    {
        0x15,  // endpoint
        0x1ED5,        // profile ID
        NULL,                     // endpoint handler
        NULL,                     // ep_state
        0x0000,                   // device ID
        0x00,                     // version
        light_show_clusters        // clusters
    },

    { WPAN_ENDPOINT_END_OF_LIST }
};

#endif

void main(void)
{
	uint8_t led_num=0;
	struct LED led[2];
	uint8_t index = 0;
	
	sys_hw_init();
	sys_xbee_init();
	
	// setup pin PTA1 to be high driving output
	PTAD &= 0xFD;
	PTADD |= 0x02;
	PTASE &= 0xFD;
	PTADS |= 0x02;
	
	// setup TPM1 to do PWM (pin 13 - PTA1 - TPM2ch0)
	// enable timer clock
	SCGC1_TPM2 = 1;
	// enable interrupt, bus clock, pre-scalar == 1
	TPM2SC = 0x48;
	// length of Timer
	TPM2MOD = TIMER_END;
	// set channel 1 as PWM
	TPM2C0SC = 0x24; // enable interrupt, PWM low->high
	// transition point
	TPM2C0V = TIMER_OFF;
	
	// initialize LEDs
	// NOTE: The LEDs need to be enumerated once they are powered on
	// You don't have to number them 0-49, other numberings can make certain
	// patterns simpler.  You'd have to cut power to reset the numbering though.
	for (index=0; index < 2; ++index) {
		// start off by setting all of the LEDs to dim blue
		// NOTE: picked a random color to make sure things were working
		// could easily default to LEDs off using brightness=0
		led[index].brightness = 0x10;
		led[index].red = 0;
		led[index].green = 0;
		led[index].blue = 1;
		led[index].extra = 0;
	}
	index = 0; // need to reset after for loop
	for (led_num=0; led_num < 50; ++led_num){
		// set the 50 LEDs to initial state
		led[index].number = led_num;
		send_led(&(led[index]));
		index ^= 1;
	}
	
	// run forever, processing incoming
	for (;;) {
		sys_watchdog_reset();
		sys_xbee_tick();
	}
		
}
