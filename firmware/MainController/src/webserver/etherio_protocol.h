/*
 * etherio_protocol.h
 *
 *  Created on: 2011-03-09
 *      Author: jsamch
 */

#ifndef __ETHERIO_PROTOCOL
#define __ETHERIO_PROTOCOL

#include "etherio_udp.h"
#include "uip_arp.h"

typedef struct etherio_hdr_st {
  struct uip_eth_hdr ethhdr;
  u16_t dataA;
  u16_t dataB;
  u8_t  dataC;
  u8_t  dataD;
} etherio_hdr_t;

void etherio_in(void);

#endif
