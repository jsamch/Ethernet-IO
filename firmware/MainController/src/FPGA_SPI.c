/*
 * FPGA Interface SPI driver
 *
 * */

#include "FreeRTOS.h"
#include "FPGA_SPI.h"
#include <stdint.h>
#include <string.h>
#include <stdio.h>

#define FPGA_SSEL (1<<6)
#define PCONP_SSP1 (1<<10)

#define SSP_SR_TFE  (1<<0)
#define SSP_SR_TNF  (1<<1)
#define SSP_SR_RNE  (1<<2)
#define SSP_SR_BUSY (1<<4)

typedef enum { RESERVED0     = 0,
	           OP_READ_ONE   = 1,
	           OP_READ_BURST = 2,
	           OP_WRITE_ONE  = 3,
	           OP_WRITE_BURST= 4,
	           OP_RW_BURST   = 5,
	           RESERVED6     = 6,
	           RESERVED7     = 7,
	           RESERVED8     = 8,
	           OP_STROBE     = 9
} FPGA_SPI_Optype;

uint16_t make_spi_op( FPGA_SPI_Optype Operation, uint16_t address ) {
  return( (Operation << 12) + address );
}

/*
 * AOut1 Green P0.28
 * AOut1 Red   P0.27
 *
 * AOut2 Green P2.11
 * AOut2 Red   P2.13
 *
 * AOut3 Green P2.4
 * AOut3 Red   P1.31
 *
 * AOut4 Green P0.22
 * AOut4 Red   P0.21
 *
 * AOut5 Green P2.12
 * AOut5 Red   P2.5
 *
 * AOut6 Green P2.8
 * AOut6 Red   P0.4
 *
 * AOut7 Green P0.16
 * AOut7 Red   P0.15
 *
 * AOut8 Green P0.18
 * AOut8 Red   P0.17
 *
 *
 * */

#define AOut8R_P0 (1<<17)
#define AOut8G_P0 (1<<18)
#define AOut7R_P0 (1<<16)
#define AOut7G_P0 (1<<15)
#define AOut6G_P2 (1<<8)
#define AOut6R_P0 (1<<4)
#define AOut5R_P2 (1<<5)
#define AOut5G_P2 (1<<12)
#define AOut4R_P0 (1<<21)
#define AOut4G_P0 (1<<22)
#define AOut3R_P1 (1<<31)
#define AOut3G_P2 (1<<4)
#define AOut2R_P2 (1<<13)
#define AOut2G_P2 (1<<11)
#define AOut1R_P0 (1<<27)
#define AOut1G_P0 (1<<28)

void leds_gpio_init(void) {
	LPC_GPIO0->FIODIR |= AOut6R_P0 + AOut7R_P0 + AOut7G_P0 + AOut8R_P0 + AOut8G_P0 + AOut4R_P0 + AOut4G_P0 + AOut1R_P0 + AOut1G_P0;
	LPC_GPIO1->FIODIR |= AOut3R_P1;
	LPC_GPIO2->FIODIR |= AOut2G_P2 + AOut2R_P2 + AOut3G_P2 + AOut5G_P2 + AOut5R_P2 + AOut6G_P2;
}

// Based on the two register value, return an integer for quadrature
int quadrature_value( uint16_t highReg, uint16_t lowReg ) {
	uint32_t fullreg;

	if( (highReg & 0x0080) > 0 ) { // Bit 24 is high (negative value)
		fullreg = 0xFF000000 | (highReg << 16 ) | lowReg;
	} else {
		fullreg = (highReg << 16 ) | lowReg;
	}
	return( (int) fullreg );
}

// Assumes that the buffer starts at address 0x000 and the howmany specifies how many registers were read
// Mode specifies the format of the output (HTML or JSON)
unsigned short dump_registers_table(char* outbuf, uint16_t* regs, char howmany, char mode ) {
	int ii;
	uint16_t prev_word;
	char tmpbuf[64];
	float voltage;


	prev_word = regs[0];

	if(mode == FPGA_SPI_HTML) {
	  strcpy(outbuf,"FPGA:<BR>");
	}
	for(ii = 0 ; ii < howmany ; ii++ ) {
		if( ii < 20 && (ii % 2) == 1 ) { // Quadratures
	      if( mode == FPGA_SPI_HTML ) {
	        sprintf(tmpbuf,"QE%d:0x%4.4X%4.4X<BR>", ii/2, prev_word, regs[ii] );
	      } else if (mode == FPGA_SPI_JSON){
	    	sprintf(tmpbuf,"\"QE%d\":%ld,\n",ii/2, quadrature_value(prev_word, regs[ii]) );
	      }

	      strcat(outbuf,tmpbuf);
		}
		if( ii >= 20 && ii < 28 ) {
		  voltage = (signed short int)regs[ii] / 32768.0 * 10.0;
		  if( mode == FPGA_SPI_HTML ) {
		    sprintf(tmpbuf,"ADC%d:0x%4.4X (%2.3f V)<BR>", ii-20, regs[ii], voltage);
		  } else if (mode == FPGA_SPI_JSON) {
			sprintf(tmpbuf,"\"ADC%d\":%ld,\n", ii-20, regs[ii] );
		  }

		  strcat(outbuf,tmpbuf);
		}
		if( ii >= 28 && ii < 36 ) {
		  if( mode == FPGA_SPI_HTML ) {
	        sprintf(tmpbuf,"DAC%d:0x%4.4X<BR>", ii-28, regs[ii]);
		  } else if (mode == FPGA_SPI_JSON ){
			sprintf(tmpbuf,"\"DAC%d\":%ld,\n", ii-28, regs[ii]);
		  }

	      strcat(outbuf,tmpbuf);
		}
		prev_word = regs[ii];
	}
	outbuf[strlen(outbuf)-2] = '\n'; // Replace last comma by a newline
	return( strlen(outbuf) );
}

// Pass it an array of 8 letters "R" Red, "G" Green or "A" Amber (G+R). 8 characters
// E.g. "GGGGRRAA"
void set_leds( char* LedString ) {
	int ii;
	// Clear all Leds
	LPC_GPIO0->FIOSET = AOut6R_P0 + AOut7R_P0 + AOut7G_P0 + AOut8R_P0 + AOut8G_P0 + AOut4R_P0 + AOut4G_P0 + AOut1R_P0 + AOut1G_P0;
	LPC_GPIO1->FIOSET = AOut3R_P1;
	LPC_GPIO2->FIOSET = AOut2G_P2 + AOut2R_P2 + AOut3G_P2 + AOut5G_P2 + AOut5R_P2 + AOut6G_P2;

	for(ii = 0 ; ii < 8 ; ii++ ) {
		if ( LedString[ii] == 'R' || LedString[ii] == 'A' ) {
			switch( ii+1 ) {
			case 1:
				LPC_GPIO0->FIOCLR = AOut1R_P0; break;
			case 2:
				LPC_GPIO2->FIOCLR = AOut2R_P2; break;
			case 3:
				LPC_GPIO1->FIOCLR = AOut3R_P1; break;
			case 4:
				LPC_GPIO0->FIOCLR = AOut4R_P0; break;
			case 5:
				LPC_GPIO2->FIOCLR = AOut5R_P2; break;
			case 6:
				LPC_GPIO0->FIOCLR = AOut6R_P0; break;
			case 7:
				LPC_GPIO0->FIOCLR = AOut7R_P0; break;
			case 8:
				LPC_GPIO0->FIOCLR = AOut8R_P0; break;
			}
		}
		if ( LedString[ii] == 'G' || LedString[ii] == 'A' ) {
			switch( ii+1 ) {
			case 1:
				LPC_GPIO0->FIOCLR = AOut1G_P0; break;
			case 2:
				LPC_GPIO2->FIOCLR = AOut2G_P2; break;
			case 3:
				LPC_GPIO2->FIOCLR = AOut3G_P2; break;
			case 4:
				LPC_GPIO0->FIOCLR = AOut4G_P0; break;
			case 5:
				LPC_GPIO2->FIOCLR = AOut5G_P2; break;
			case 6:
				LPC_GPIO2->FIOCLR = AOut6G_P2; break;
			case 7:
				LPC_GPIO0->FIOCLR = AOut7G_P0; break;
			case 8:
				LPC_GPIO0->FIOCLR = AOut8G_P0; break;
			}
		}
	}
}


void spi_block_transfer( uint16_t* TxBuffer, uint16_t* RxBuffer, uint16_t transfer_size) {
  // Watch out to ensure that the transfer size will be equal or less than Tx and Rx buffer sizes
	int txptr, rxptr, remaintx, remainrx;
	// Ensure any pending transfers are completed
	while( ( LPC_SSP1->SR & SSP_SR_TFE ) == 0 );
	txptr = 0; rxptr = 0; // Init pointers
	remaintx = transfer_size;
	remainrx = transfer_size;

	// Chip select down (start of transfer)
	LPC_GPIO0->FIOCLR = FPGA_SSEL;

	while( remaintx > 0 ) {
		if ( LPC_SSP1->SR & SSP_SR_TNF ) { // Keep filling until full
			LPC_SSP1->DR = TxBuffer[txptr++] & 0x0000FFFF;
			remaintx--;
			if (LPC_SSP1->SR & SSP_SR_RNE ) {
			  RxBuffer[rxptr++] = LPC_SSP1->DR;
			  remainrx--;
			}
		} else {
			// Schedule some sleep ?
		}
	}
	// Now that all have been pushed into FIFO, we need to wait for the remaining rx to come back
	while( remainrx > 0 ) {
		if (LPC_SSP1->SR & SSP_SR_RNE ) {
			RxBuffer[rxptr++] = LPC_SSP1->DR;
			remainrx--;
		} else {
		    // Schedule some sleep ?
		}
	}

	// Chip select up (end of transfer)
	LPC_GPIO0->FIOSET = FPGA_SSEL;
}

// This assumes that the SPI unit has previously been initialised.
uint16_t fpga_spi_single_read( uint16_t address ) {
	uint16_t txbuf[3];
	uint16_t rxbuf[3];

	txbuf[0] = make_spi_op( OP_READ_ONE, address );
	spi_block_transfer( txbuf, rxbuf, 3 );
	// rxbuf[0] = FPGA Status, rxbuf[1] = invalid, rxbuf[2] = read data
	return( rxbuf[2] );
}

// Returns the status of the FPGA (may be discarded if not needed)
uint16_t fpga_spi_single_write( uint16_t address, uint16_t data ) {
	uint16_t txbuf[2];
	uint16_t rxbuf[2];

	txbuf[0] = make_spi_op( OP_WRITE_ONE, address );
	txbuf[1] = data;
	spi_block_transfer( txbuf, rxbuf, 2);

	return(rxbuf[0]);
}

// Returns the status and re-aligns the received data so that rd_data[0] corresponds to the base address read
// (the SPI does make an offset of 3 words (status + 2 words delay) in burst read/write mode
uint16_t fpga_spi_rw_burst( uint16_t* wr_data, uint16_t* rd_data, uint16_t baseaddress, uint16_t burst_size ) {
	uint16_t txbuf[burst_size+3];
	uint16_t rxbuf[burst_size+3];  // Watch out for stack usage
	int ii;

	// Prepare tx buffer
	txbuf[0] = make_spi_op( OP_RW_BURST, baseaddress );
	for(ii = 0 ; ii < burst_size ; ii++ ) {
		txbuf[ii+1] = wr_data[ii];
	}

	spi_block_transfer( txbuf, rxbuf, burst_size+3 ); // +3 because of pipeline effect of SPI

	// Realigns RX results
	for(ii = 0 ; ii < burst_size ; ii++ ) {
		rd_data[ii] = rxbuf[ii+3];
	}

	return( rxbuf[0] );
}

uint16_t fpga_spi_read_burst( uint16_t* rd_data, uint16_t baseaddress, uint16_t burst_size ) {
	uint16_t txbuf[burst_size+3];
	uint16_t rxbuf[burst_size+3];  // Watch out for stack usage
	int ii;
	txbuf[0] = make_spi_op( OP_READ_BURST, baseaddress );

	spi_block_transfer( txbuf, rxbuf, burst_size+3 );

	// Realigns RX results
	for(ii = 0 ; ii < burst_size ; ii++ ) {
		rd_data[ii] = rxbuf[ii+2];
	}

	return( rxbuf[0] );
}



void fpga_spi_init(void) {
	// LPC_PCONP already enables bit  PCSSP1 to enable the SSP1 on reset
	LPC_SC->PCONP |= PCONP_SSP1;
	LPC_SC->PCLKSEL0 &= ~0x00300000;    // PCLK for SSP1 is 120 MHz / 4 = 30 MHz
	LPC_PINCON->PINMODE0 |= 0x000C0000; // PULL Down on MOSI.
	LPC_PINCON->PINSEL0 &= ~0x000FF000; // Pins for SPI (clear previous config)
	LPC_PINCON->PINSEL0  |= 0x000A8000;  // SPI Mode (SSEL is still a GPIO to support the burst transfers)
	LPC_GPIO0->FIODIR |= FPGA_SSEL;
	//LPC_SSP1->CPSR = 2;  // Divide by 2 the clock (yield 15 MHz for a 30 MHz PCLK)
	LPC_SSP1->CPSR = 30;  // Divide by 10 the clock (yield 1 MHz for a 30 MHz PCLK)
	LPC_SSP1->CR0 = 0x0000000F; // DSS=16-bit transfers
	LPC_SSP1->CR1 = 0x00000002; // SSP is enabled
}

void fpga_spi_transfer_test(void) {
	while( ( LPC_SSP1->SR & SSP_SR_BUSY ) != 0 ); // Wait until not busy
	LPC_GPIO0->FIOCLR = FPGA_SSEL;
	LPC_SSP1->DR = 0x0000A50F;
	LPC_SSP1->DR = 0x00005555;
	LPC_GPIO0->FIOSET = FPGA_SSEL;
	while( ( LPC_SSP1->SR & SSP_SR_BUSY ) != 0 ); // Wait until not busy
}

void fpga_spi_long_transfer_test(void) {
	int ii;
	int waitcnt;
	int finalsr;
	short int rxbuf[110];
	int rxptr;
	waitcnt = 0;
	rxptr = 0;
	while( ( LPC_SSP1->SR & SSP_SR_TFE ) == 0 );
	LPC_GPIO0->FIOCLR = FPGA_SSEL;
	for(ii = 0 ; ii <110 ; ii++) {
		rxbuf[ii] = 0xDEAD;
	}
	ii = 0;
	while(ii < 100) {
		if ( LPC_SSP1->SR & SSP_SR_TNF ) { // Keep filling until full
			LPC_SSP1->DR = ii & 0x0000FFFF;
			ii++;
			if (LPC_SSP1->SR & SSP_SR_RNE ) {
			  rxbuf[rxptr++] = LPC_SSP1->DR;
			}
		}
	}
	finalsr = LPC_SSP1->SR;
	while( ( LPC_SSP1->SR & SSP_SR_BUSY ) != 0 ); // Wait until not busy to purge FIFO
	while( LPC_SSP1->SR & SSP_SR_RNE ) {
		rxbuf[rxptr++] = LPC_SSP1->DR;  // Gorge up the last bits of data
	}
	LPC_GPIO0->FIOSET = FPGA_SSEL;
}




