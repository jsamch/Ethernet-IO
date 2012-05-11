/*
 * etherio_udp.h
 *
 *  Created on: 2011-11-30
 *      Author: jsamch
 */

#ifndef ETHERIO_UDP_H_
#define ETHERIO_UDP_H_

#include "uip.h"


#define ETHERIO_MODE_UNDEF   0 /* Uninitialized ?                                  */
#define ETHERIO_MODE_SLAVE   1 /* Slave mode                                       */
#define ETHERIO_MODE_MASTER  2 /* Master Mode - Will autonomously send status info */

struct etherio_state_t {
	struct uip_udp_conn *conn;

	unsigned char etherio_mode;       /* Master or slave mode - slave mode from init*/
	unsigned int  master_mode_rate;   /* Update rate (Hz) */
	uip_ipaddr_t  master_mode_dest;   /* IP address of recipient in master mode */
	u16_t         master_mode_port;   /* UDP port of master mode recipient      */
};



void etherio_udp_init(void);

void etherio_appcall(void);

void etherio_set_mastermode( unsigned int rate, uip_ipaddr_t dst_IP, u16_t dst_port );
void etherio_set_slavemode();

/* Return the current mode of operation (slave or master mode) */
unsigned char etherio_get_mode();

#endif /* ETHERIO_UDP_H_ */
