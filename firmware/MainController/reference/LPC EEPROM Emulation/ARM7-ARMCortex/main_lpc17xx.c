/**************************************************************************
MODULE:       MAIN - LPC17xx Version
CONTAINS:     Demonstration of non-volatile storage in flash memory
              Reset the board and the count shown on the LEDs will
			  continue where it left off
			  Erase all flash memory when programming

              Written for the Keil MCB1700 board

DEVELOPED BY: Embedded Systems Academy, Inc. 2010
              www.esacademy.com
COPYRIGHT:    NXP Semiconductors, 2010. All rights reserved.
VERSION:      1.00
***************************************************************************/ 

#include "LPC17xx.h"
#include "system_LPC17xx.h"
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
void __irq TIMER0_IRQHandler (
  void
  ) 
{
  // clear interrupt flag
  LPC_TIM0->IR = 1;
 
  // increment counter and store in non-volatile memory
  Counter++;
  if (!NVOL_SetVariable(COUNTER, (UNSIGNED8 *)&Counter, sizeof(Counter)))
  {
    while(1);
  }

  // show counter on LEDs  
  LPC_GPIO1->FIOCLR = 0xBUL << 28;
  LPC_GPIO2->FIOCLR = 0x1FUL << 2;
  LPC_GPIO1->FIOSET = ((Counter & 0x04) << 29) | ((Counter & 0x03) << 28);
  LPC_GPIO2->FIOSET = (Counter & 0xF8) >> 1;
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
 
  // configure P1.28, P1.29 and P1.31 as digital outputs (no pull-up/down)
  LPC_PINCON->PINSEL3 &= ~(0xCFUL << 24);
  LPC_PINCON->PINMODE3 &= ~(0xCFUL << 24);
  LPC_PINCON->PINMODE3 |= (0x8AUL << 24);
  LPC_GPIO1->FIODIR |= (0xBUL << 28);

  // configure P2.2 - P2.6 as digital outputs (no pull-up/down)
  LPC_PINCON->PINSEL4 &= ~(0x3FFUL << 4);
  LPC_PINCON->PINMODE4 &= ~(0x3FFUL << 4);
  LPC_PINCON->PINMODE4 |= (0x2AAUL << 4);
  LPC_GPIO2->FIODIR |= (0x1FUL << 2); 

  // initialize timer
  LPC_TIM0->PR  = 1000;                                    // divide by 1000 = 18kHz
  LPC_TIM0->MR0 = 899;                                     // count up every 20ms
  LPC_TIM0->MCR = 3;                                       // interrupt and Reset on MR0
  LPC_TIM0->TCR = 1;                                       // timer 0 Enable

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
  NVIC_EnableIRQ(TIMER0_IRQn);
  NVIC_SetPriority(TIMER0_IRQn, 10);

  // loop forever
  while (1);
}
