/**************************************************************************
MODULE:       MAIN - LPC23xx Version
CONTAINS:     Demonstration of non-volatile storage in flash memory
              Reset the board and the count shown on the LEDs will
			  continue where it left off
			  Erase all flash memory when programming

              Written for the Keil MCB2300 board.

DEVELOPED BY: Embedded Systems Academy, Inc. 2010
              www.esacademy.com
COPYRIGHT:    NXP Semiconductors, 2010. All rights reserved.
VERSION:      1.00
***************************************************************************/ 
	
#include "LPC23xx.h"
#include "flash_nvol.h"

// a unique identifier for the non-volatile variable
#define COUNTER 1

// an 8-bit counter
static volatile UNSIGNED8 Counter;

// disable code read protection
const unsigned long crp __attribute__ ((at(0x1FC))) = 0x00000000;

/**************************************************************************
DOES:    Timer interrupt handler
         Increases counter, displays count on LEDs and
		 stores count in non-volatile memory
**************************************************************************/
void __irq TIMER0_IRQHandler (
  void
  ) 
{
  // clear interrupt flag
  T0IR = 1;
 
  // increment counter and store in non-volatile memory
  Counter++;
  if (!NVOL_SetVariable(COUNTER, (UNSIGNED8 *)&Counter, sizeof(Counter)))
  {
    while(1);
  }

  // show counter on LEDs
  FIO2CLR = 0x000000FF;
  FIO2SET = Counter & 0xFF;

  // ack interrupt
  VICVectAddr = 0xFFFFFFFF;
}

/**************************************************************************
DOES:    Program entry point
         Demonstration of non-volatile memory
**************************************************************************/
int main
  (
  void
  )
{					
  // disable all interrupts
  VICIntEnClr = 0xFFFFFFFF;
  VICIntSelect = 0x00000000;

  // configure P2.0 - P2.7 as digital outputs (no pull-up/down)
  PINMODE4 = 0x0000AAAA;
  FIO2DIR = 0x000000FF;

  // initialize timer
  T0PR  = 1000;                                            // divide by 1000 = 12kHz
  T0MR0 = 599;											   // count up every 20ms
  T0MCR = 3;                                               // interrupt and reset on MR0
  T0TCR = 1;                                               // timer 0 enable

  // initialize non-volatile memory
  if (!NVOL_Init())
  {
    // error
    while(1);
  }

  // get the last value of the counter or set to zero if not found
  if (!NVOL_GetVariable(COUNTER, (UNSIGNED8 *)&Counter, sizeof(Counter)))
  {
    Counter = 0;
  }

  // init interrupts
  VICVectAddr4  = (unsigned long) TIMER0_IRQHandler;       // set interrupt vector
  VICVectCntl4  = 3;                                       // priority
  VICIntEnable  = (1 << 4);                                // enable timer 0 interrupt

  // loop forever
  while (1);
}
