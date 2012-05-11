/*
 * etherio_udp.c
 *
 *  Created on: 2011-11-30
 *      Author: jsamch
 */

#include <stdio.h>
#include <string.h>
#include "uip.h"
#include "udpd.h"
#include "etherio_udp.h"
#include "FPGA_SPI.h"
#include "FreeRTOSConfig.h"
#include "FreeRTOS.h"

#define ETHERIO_DATA_PORT 1234

#define ETHERIO_MAGIC     0xCA
#define ETHERIO_PROT_VER  0x21

#define IOUPDATE_PKT_TYPE 0x01
#define IOUPDATE_PKT_RESP 0x81
#define DAC_CFG_PKT_TYPE  0x05
#define DAC_CFG_RESP      0x85
#define ERROR_PKT_TYPE    0xF0

/* EtherIO State information global variable */
struct etherio_state_t etherio_state;


struct etherio_msg {
  uint8_t  magic;
  uint8_t  version;
  uint8_t  type;
  uint8_t  pad;
  uint16_t sequence;
  uint16_t data[32];
};

int parse_msg(void)
{
  struct etherio_msg *m = (struct etherio_msg *)uip_appdata;

  //if(m->op == 0xAB )
    return uip_datalen();
  //}

}

void etherio_set_mastermode( unsigned int rate, uip_ipaddr_t dst_IP, u16_t dst_port ) {
	etherio_state.etherio_mode     = ETHERIO_MODE_MASTER;
	etherio_state.master_mode_rate = rate;
	uip_ipaddr_copy( &etherio_state.master_mode_dest, &dst_IP );
	etherio_state.master_mode_port = dst_port;
}


void etherio_set_slavemode(){
	etherio_state.etherio_mode = ETHERIO_MODE_SLAVE;
}

unsigned char etherio_get_mode() {
	return(etherio_state.etherio_mode);
}


void etherio_udp_init(void) {
	  uip_ipaddr_t addr;

	  uip_ipaddr(addr, 255,255,255,255 );
	  etherio_state.conn = uip_udp_new(&addr, HTONS(ETHERIO_DATA_PORT));
	  if(etherio_state.conn != NULL) {
	    uip_udp_bind(etherio_state.conn, HTONS(ETHERIO_DATA_PORT));
	  }

	  etherio_set_slavemode();
}

static u8_t *
add_msg_type(u8_t *optptr, u8_t type)
{
  *optptr++ = 1;
  *optptr++ = type;
  return optptr;
}

static char * inv_pkt_resp = "Invalid Packet (Magic or Version)";

#define SPI_TRANSFER_SIZE 28

static void send_response(int size) {
  int len, ii;
  uint16_t status;
  struct etherio_msg *m = (struct etherio_msg *)uip_appdata;
  void * seqaddr  = &m->sequence;
  void * dataaddr = &m->data;

  uint16_t fpga_tx_buffer[SPI_TRANSFER_SIZE];
  uint16_t fpga_rx_buffer[SPI_TRANSFER_SIZE];

  // Initialise buffers
  for( ii = 0 ; ii < SPI_TRANSFER_SIZE ; ii++ ) {
	  fpga_tx_buffer[ii] = 0;
	  fpga_rx_buffer[ii] = 0;
  }

  len = 6;  // Starts with minimally MAGIC + VER + TYPE + PAD + SEQ(2)
  if( m->magic == ETHERIO_MAGIC && m-> version == ETHERIO_PROT_VER ) {
	  switch( m->type ) {
		  case IOUPDATE_PKT_TYPE:
			  m->type = IOUPDATE_PKT_RESP;
			  m->pad  = 0xAA;
			  // Copy DAC values and write to proper location in SPI buffer
			  for(ii = 0 ; ii < 8 ; ii++ ) {
				  fpga_tx_buffer[FPGA_SPI_DACOFFSET+ii] = ntohs(m->data[ii]);
			  }

			  fpga_spi_rw_burst( fpga_tx_buffer, fpga_rx_buffer, 0, SPI_TRANSFER_SIZE );
			  for(ii = 0; ii < 28 ; ii++ ) {
				  m->data[ii] = 0xAAAA;
			  }
			  for(ii = 0; ii < 20+8 ; ii++) {
				m->data[ii]   = htons(fpga_rx_buffer[ii]);
			  }
			  len += (20+8)*2;
			  break;
		  case DAC_CFG_PKT_TYPE:
			  m->type = DAC_CFG_RESP;
			  m->pad  = 0xAA;
			  // Replace by proper hook to update led colors based on DAC config.
			  status = fpga_spi_single_write(40,m->data[0]);
   			  vTaskDelay(20000/portTICK_RATE_US);
			  status = fpga_spi_single_write(41,m->data[1]);

			  m->data[0] = htons(status);
			  m->data[1] = htons(0xDEAD);
			  len += 4;
	  }
  } else {
	  m->magic   = ETHERIO_MAGIC;
	  m->version = ETHERIO_PROT_VER;
	  m->type    = ERROR_PKT_TYPE; // Indicates an Error

	  len += strlen(inv_pkt_resp);
	  strcpy( (char*)&m->data, inv_pkt_resp);
  }

  uip_send(uip_appdata, len );
}


void etherio_appcall(void) {
	// s->conn is our local udp connection.
	int msg_size;

	msg_size = parse_msg();

	//printf("Got %d UDP bytes to parse\n", msg_size);

	send_response(msg_size);

}

