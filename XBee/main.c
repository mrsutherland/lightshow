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

//#define SET_HIGH (PTAD |= 0x08)
//#define SET_LOW (PTAD &= ~0x08)

// timer settings for different bits
#define TIMER_0 240
#define TIMER_1 480
#define TIMER_END 720  // modulo number
#define TIMER_OFF TIMER_END+1

void _delay_10_us(void) {
	uint8_t i;
	for(i=0; i<DELAY_us; ++i);
}

struct LED {
	uint8_t number;
	uint8_t brightness;
	uint8_t green:4;
	uint8_t blue:4;
	uint8_t extra:4;
	uint8_t red:4;
};

#define BLUE 0
#define GREEN 1
#define RED 2

// Buffer for interrupt
struct LED *cur_led;
uint8_t led_cur_byte;
uint8_t led_bit_mask;
uint16_t led_next_bit = TIMER_OFF;

//interrupt 9 void Vtpm2ch1_isr(void)
#pragma TRAP_PROC
interrupt void Vtpm2ovf_isr(void)
{
	// reset interrupt
	//TPM2C1SC_CH1F=0; // Read flag, then write a 0 to the bit.
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
		led_next_bit = TIMER_OFF;
	}
}

void send_led(struct LED* next_led) 
{
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
	struct LED *next_led;
	uint8_t index = 0;
	uint8_t red = 0;
	uint8_t blue = 0;
	uint8_t green = 0;
	uint8_t brightness = 0xFF;
	uint16_t i;
	uint8_t offset = 0;
	
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
	TPM2SC = 0x48;//0x08; //0x48;
	// length of Timer
	TPM2MOD = TIMER_END;
	// set channel 1 as PWM
	TPM2C0SC = 0x24;//0x64; // enable interrupt, PWM low->high
	// transition point
	TPM2C0V = TIMER_OFF;
	
	// initialize LEDs
	red = 0x1;
	green = 0x1;
	blue = 0x1;
	brightness = 0x10;
	for (led_num=0; led_num < 50; ++led_num){
		next_led = &(led[index]);
		next_led->number = led_num;
		next_led->brightness = brightness;
		next_led->blue = blue;
		next_led->green = green;
		next_led->red = red;
		next_led->extra = 0x00;
		send_led(next_led);
		index ^= 1;
	}
	
	for (;;) {
		sys_watchdog_reset();
		sys_xbee_tick();
	}
		
}
