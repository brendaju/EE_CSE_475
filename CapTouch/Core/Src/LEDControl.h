/*
  WS2812B CPU and memory efficient library
  Date: 28.9.2016
  Author: Martin Hubacek
  	  	  http://www.martinhubacek.cz
  	  	  @hubmartin
  Licence: MIT License
*/

#ifndef LEDCONTROL_H_
#define LEDCONTROL_H_

#include <stdint.h>

void visInit();
void visHandle(uint16_t *input, uint8_t* gridLoc, uint8_t newTouch);
#endif /* LEDCONTROL_H_ */
