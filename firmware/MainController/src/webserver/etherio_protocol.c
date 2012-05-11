/*
 * etherio_protocol.c
 *
 *  Created on: 2011-03-09
 *      Author: jsamch
 */

#include <stdio.h>

#include "etherio_protocol.h"


#define BUF   ((etherio_hdr_t*)&uip_buf[0])

void etherio_in(void) {
	etherio_hdr_t* data;

	data = (etherio_hdr_t*)uip_buf;

	printf("DatA=%d;DatB=%d\n", BUF->dataA, BUF->dataB);
}
