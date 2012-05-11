/*
 * FPGA_SPI.h
 *
 *  Created on: 2011-11-06
 *      Author: jsamch
 */


#ifndef FPGA_SPI_H_
#define FPGA_SPI_H_


#define FPGA_SPI_DACOFFSET 20
#define FPGA_SPI_QUADRDOFFSET 0
#define FPGA_SPI_NUMQUADR  10
#define FPGA_SPI_ADCOFFSET 20

#define FPGA_SPI_HTML 0
#define FPGA_SPI_JSON 1

void leds_gpio_init(void);

void set_leds( char* ledString );

unsigned short dump_registers_table(char* outbuf, uint16_t* regs, char howmany, char mode );

void fpga_spi_init(void);

uint16_t fpga_spi_single_read( uint16_t address );

uint16_t fpga_spi_single_write( uint16_t address, uint16_t data );

uint16_t fpga_spi_rw_burst( uint16_t* wr_data, uint16_t* rd_data, uint16_t baseaddress, uint16_t burst_size );

uint16_t fpga_spi_read_burst( uint16_t* rd_data, uint16_t baseaddress, uint16_t burst_size );

void fpga_spi_transfer_test(void);

void fpga_spi_long_transfer_test(void);

#endif /* FPGA_SPI_H_ */
