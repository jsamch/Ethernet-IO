/* EtherIO Controller */

/* Standard includes. */
#include "stdio.h"

/* Scheduler includes. */
#include "FreeRTOS.h"
#include "task.h"

#include "FPGA_SPI.h"
#include "etherio_udp.h"

#include "LPC17xx.h"
#include "system_LPC17xx.h"
#include "flash_nvol.h"

/* Red Suite includes. */
//#include "lcd_driver.h"
//#include "lcd.h"

/*-----------------------------------------------------------*/

/* The time between cycles of the 'check' functionality (defined within the
tick hook. */
#define mainCHECK_DELAY						( ( portTickType ) 5000000 / portTICK_RATE_US )

/* Task priorities. */

#define mainUIP_TASK_PRIORITY				( tskIDLE_PRIORITY + 3 )
#define mainFPGA_TASK_PRIORITY				( tskIDLE_PRIORITY + 4 )

/* The WEB server has a larger stack as it utilises stack hungry string
handling library calls. */
#define mainBASIC_WEB_STACK_SIZE            ( 2048 )

/* The message displayed by the WEB server when all tasks are executing
without an error being reported. */
#define mainPASS_STATUS_MESSAGE				"All tasks are executing without error."

/* Bit definitions. */
#define PCONP_PCGPIO    0x00008000
#define PLLFEED_FEED1   0x000000AA
#define PLLFEED_FEED2   0x00000055
/*-----------------------------------------------------------*/

/*
 * Configure the hardware for the demo.
 */
static void prvSetupHardware( void );

/*
 * The task that handles the uIP stack.  All TCP/IP processing is performed in
 * this task.
 */
extern void vuIP_Task( void *pvParameters );

/*
 * The task that handles the USB stack.
 */
extern void vUSBTask( void *pvParameters );

/*
 * Simply returns the current status message for display on served WEB pages.
 */
char *pcGetTaskStatusMessage( void );

/*-----------------------------------------------------------*/

/* Holds the status message displayed by the WEB server. */
static char *pcStatusMessage = mainPASS_STATUS_MESSAGE;

/*-----------------------------------------------------------*/

#define TEST_PIN ( 1UL << 9UL )   // Port 2
#define REF_PIN  ( 1UL << 22UL )  // Port 0

//static int cnt;

void vFPGA_test_task( void *pvParameters )
{
	uint16_t status, value;

	uint16_t tx_data[64];
	uint16_t rx_data[64];
	int ii;

	vTaskDelay(500000/portTICK_RATE_US);
	set_leds("GGGGGGGG");

	for(ii = 0 ; ii < 64 ; ii++ ) {
		tx_data[ii] = 0x0000;
	}

	// Program the DACs to output 2.5V
	for(ii = 20 ; ii < 28 ; ii++ ) {
		tx_data[ii] = 0x4000;
	}


	status = fpga_spi_rw_burst(tx_data, rx_data, 0x00, 28);


	vTaskDelay(500000/portTICK_RATE_US);
	set_leds("RGRGRGRG");
	// Configure the 8 DACs
	status = fpga_spi_single_write(40,0x8888);
	vTaskDelay(20000/portTICK_RATE_US);

	status = fpga_spi_single_write(41,0x8888);

	vTaskDelay(20000/portTICK_RATE_US);
	set_leds("AAAAAAAA");

	vTaskDelay(500000/portTICK_RATE_US);
	set_leds("00000000");
	status = fpga_spi_rw_burst(tx_data, rx_data, 0x00, 28);
	vTaskDelay(500000/portTICK_RATE_US);

	set_leds("GGGGGGGG");

    for( ;; )
    {
    	vTaskDelay(1000000/portTICK_RATE_US);

    	//dump_registers_table(rx_data, 28);


//    	vTaskDelay(100);
//    	status = fpga_spi_rw_burst(tx_data, rx_data, 0x00, 28);
//    	vTaskDelay(100);
//    	value  = fpga_spi_single_read(32);
    }
}

int main( void )
{
	char cIPAddress[ 16 ]; /* Enough space for "xxx.xxx.xxx.xxx\0". */




	/* Configure the hardware for use by this demo. */
	prvSetupHardware();

	fpga_spi_init();
	leds_gpio_init();

#if 0 // Broken
	// initialize non-volatile memory
	if (!NVOL_Init())
	{
		// error
		while(1);
	}
#endif

	set_leds("00000000");



	printf("EtherIO Controller Starting\n");
	sprintf( cIPAddress, "%d.%d.%d.%d", configIP_ADDR0, configIP_ADDR1, configIP_ADDR2, configIP_ADDR3 );
	printf( "IP Address = %s\n", cIPAddress );

	/* Web server and IP task */
    xTaskCreate( vuIP_Task, ( signed char * ) "uIP", mainBASIC_WEB_STACK_SIZE, ( void * ) NULL, mainUIP_TASK_PRIORITY, NULL );

    /* FPGA Initialization and maintenance task */
    xTaskCreate( vFPGA_test_task , ( signed char * ) "FPGA_IO", 1024, ( void * ) NULL, mainFPGA_TASK_PRIORITY, NULL );

    /* Start the scheduler. */
    printf("Scheduler will start now\n");
	vTaskStartScheduler();

    /* Will only get here if there was insufficient memory to create the idle
    task.  The idle task is created within vTaskStartScheduler(). */
	for( ;; );

}
/*-----------------------------------------------------------*/



void vApplicationTickHook( void )
{

	/* Called from every tick interrupt */

	;

}
/*-----------------------------------------------------------*/

char *pcGetTaskStatusMessage( void )
{
	/* Not bothered about a critical section here. */
	return pcStatusMessage;
}
/*-----------------------------------------------------------*/

void prvSetupHardware( void )
{
	/* Disable peripherals power. */
	LPC_SC->PCONP = 0;

	/* Enable GPIO power. */
	LPC_SC->PCONP = PCONP_PCGPIO;

	/* Disable TPIU. */
	LPC_PINCON->PINSEL10 = 0;

	if ( LPC_SC->PLL0STAT & ( 1 << 25 ) )
	{
		/* Enable PLL, disconnected. */
		LPC_SC->PLL0CON = 1;
		LPC_SC->PLL0FEED = PLLFEED_FEED1;
		LPC_SC->PLL0FEED = PLLFEED_FEED2;
	}
	
	/* Disable PLL, disconnected. */
	LPC_SC->PLL0CON = 0;
	LPC_SC->PLL0FEED = PLLFEED_FEED1;
	LPC_SC->PLL0FEED = PLLFEED_FEED2;
	    
	/* Enable main OSC. */
	LPC_SC->SCS |= 0x20;
	while( !( LPC_SC->SCS & 0x40 ) );
	
	/* select main OSC, 12MHz, as the PLL clock source. */
	LPC_SC->CLKSRCSEL = 0x1;
	
	//LPC_SC->PLL0CFG = 0x00020031;
        LPC_SC->PLL0CFG = 0x0002003B; // M = 60, N=3 => Fcco=480 MHz
	LPC_SC->PLL0FEED = PLLFEED_FEED1;
	LPC_SC->PLL0FEED = PLLFEED_FEED2;
	      
	/* Enable PLL, disconnected. */
	LPC_SC->PLL0CON = 1;
	LPC_SC->PLL0FEED = PLLFEED_FEED1;
	LPC_SC->PLL0FEED = PLLFEED_FEED2;
	
	/* Set clock divider. */
	LPC_SC->CCLKCFG = 0x03; // Fcco = 480 MHz => CCLK = 480 / 4 = 120 MHz
	
	/* Configure flash accelerator. */
	LPC_SC->FLASHCFG = 0x403a; // Flash access uses 5 CCLK cycles (good for up to 120 MHz)
	
	/* Check lock bit status. */
	while( ( ( LPC_SC->PLL0STAT & ( 1 << 26 ) ) == 0 ) );
	    
	/* Enable and connect. */
	LPC_SC->PLL0CON = 3;
	LPC_SC->PLL0FEED = PLLFEED_FEED1;
	LPC_SC->PLL0FEED = PLLFEED_FEED2;
	while( ( ( LPC_SC->PLL0STAT & ( 1 << 25 ) ) == 0 ) );

	
	
	
	/* Configure the clock for the USB. */
	  
	if( LPC_SC->PLL1STAT & ( 1 << 9 ) )
	{
		/* Enable PLL, disconnected. */
		LPC_SC->PLL1CON = 1;
		LPC_SC->PLL1FEED = PLLFEED_FEED1;
		LPC_SC->PLL1FEED = PLLFEED_FEED2;
	}
	
	/* Disable PLL, disconnected. */
	LPC_SC->PLL1CON = 0;
	LPC_SC->PLL1FEED = PLLFEED_FEED1;
	LPC_SC->PLL1FEED = PLLFEED_FEED2;
	
	LPC_SC->PLL1CFG = 0x23;
	LPC_SC->PLL1FEED = PLLFEED_FEED1;
	LPC_SC->PLL1FEED = PLLFEED_FEED2;
	      
	/* Enable PLL, disconnected. */
	LPC_SC->PLL1CON = 1;
	LPC_SC->PLL1FEED = PLLFEED_FEED1;
	LPC_SC->PLL1FEED = PLLFEED_FEED2;
	while( ( ( LPC_SC->PLL1STAT & ( 1 << 10 ) ) == 0 ) );
	
	/* Enable and connect. */
	LPC_SC->PLL1CON = 3;
	LPC_SC->PLL1FEED = PLLFEED_FEED1;
	LPC_SC->PLL1FEED = PLLFEED_FEED2;
	while( ( ( LPC_SC->PLL1STAT & ( 1 << 9 ) ) == 0 ) );

	/*  Setup the peripheral bus to be the same as the PLL output. */
	LPC_SC->PCLKSEL0 = 0x05555555;

}
/*-----------------------------------------------------------*/

void vApplicationStackOverflowHook( xTaskHandle *pxTask, signed char *pcTaskName )
{
	/* This function will get called if a task overflows its stack. */

	( void ) pxTask;
	( void ) pcTaskName;

	for( ;; );
}
/*-----------------------------------------------------------*/

void vConfigureTimerForRunTimeStats( void )
{
const unsigned long TCR_COUNT_RESET = 2, CTCR_CTM_TIMER = 0x00, TCR_COUNT_ENABLE = 0x01;

	/* This function configures a timer that is used as the time base when
	collecting run time statistical information - basically the percentage
	of CPU time that each task is utilising.  It is called automatically when
	the scheduler is started (assuming configGENERATE_RUN_TIME_STATS is set
	to 1). */

	/* Power up and feed the timer. */
	LPC_SC->PCONP |= 0x02UL;
	LPC_SC->PCLKSEL0 = (LPC_SC->PCLKSEL0 & (~(0x3<<2))) | (0x01 << 2);

	/* Reset Timer 0 */
	LPC_TIM0->TCR = TCR_COUNT_RESET;

	/* Just count up. */
	LPC_TIM0->CTCR = CTCR_CTM_TIMER;

	/* Prescale to a frequency that is good enough to get a decent resolution,
	but not too fast so as to overflow all the time. */
	LPC_TIM0->PR =  ( configCPU_CLOCK_HZ / 10000UL ) - 1UL;

	/* Start the counter. */
	LPC_TIM0->TCR = TCR_COUNT_ENABLE;
}
/*-----------------------------------------------------------*/

