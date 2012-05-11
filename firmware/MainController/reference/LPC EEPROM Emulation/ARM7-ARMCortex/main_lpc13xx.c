/**************************************************************************
MODULE:       MAIN - LPC13xx Version
CONTAINS:     Demonstration of non-volatile storage in flash memory
              Reset the board and the count shown on the LEDs will
			  continue where it left off
			  Erase all flash memory when programming

              Written for the NXP LPC1000 Evaluation Board
			  Connect P1.8 to LED1, P1.9 to LED2, P1.10 to LED3 and
			  P1.11 to LED4

DEVELOPED BY: Embedded Systems Academy, Inc. 2010
              www.esacademy.com
COPYRIGHT:    NXP Semiconductors, 2010. All rights reserved.
VERSION:      1.00
***************************************************************************/ 

#include "LPC13xx.h"
#include "system_LPC13xx.h"
#include "flash_nvol.h"

// a unique identifier for the non-volatile variable
#define COUNTER 1

// an 8-bit counter
static volatile UNSIGNED8 Counter;

/**************************************************************************
DOES:    Timer interrupt handler
         Increases counter, displays count on LEDs and
		 stores count in non-volatile memory
**************************************************************************/
void __irq TIMER32_0_IRQHandler (
  void
  ) 
{
  // clear interrupt flag
  LPC_TMR32B0->IR = 1;
 
  // increment 4-bit counter and store in non-volatile memory
  Counter++;
  if (Counter > 0xF) Counter = 0x0;
  if (!NVOL_SetVariable(COUNTER, (UNSIGNED8 *)&Counter, sizeof(Counter)))
  {
    while(1);
  }

  // show counter on LEDs
  LPC_GPIO1->DATA &= ~(0xFUL << 8);
  LPC_GPIO1->DATA |= (Counter & 0xF) << 8;
}

/**************************************************************************
DOES:    Program extry point
         Demonstration of non-volatile memory
**************************************************************************/
int main
  (
  void
  )
{
  // initialize microcontroller
  SystemInit();
 
  // configure P1.8 - P1.11 as digital outputs
  LPC_GPIO1->DIR = 0x0F00;

  // initialize timer
  LPC_TMR32B0->PR  = 1000;                                    // divide by 1000 = 18kHz
  LPC_TMR32B0->MR0 = 1299;                                    
  LPC_TMR32B0->MCR = 3;                                       // interrupt and Reset on MR0
  LPC_TMR32B0->TCR = 1;                                       // timer 0 Enable

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

  // enable timer interrupt with priority of 10
  NVIC_EnableIRQ(TIMER_32_0_IRQn);
  NVIC_SetPriority(TIMER_32_0_IRQn, 10);

  // loop forever
  while (1);
}
