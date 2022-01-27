/*
  WS2812B CPU and memory efficient library
  Date: 28.9.2016
  Author: Martin Hubacek
  	  	  http://www.martinhubacek.cz
  	  	  @hubmartin
  Licence: MIT License
*/

#include <stdint.h>

#include "stm32f4xx_hal.h"
#include "ws2812b.h"
#include <stdlib.h>

// RGB Framebuffers
uint8_t frameBuffer[3*192];
uint8_t frameBuffer2[3*20];


// Helper defines
#define newColor(r, g, b) (((uint32_t)(r) << 16) | ((uint32_t)(g) <<  8) | (b))
#define Red(c) ((uint8_t)((c >> 16) & 0xFF))
#define Green(c) ((uint8_t)((c >> 8) & 0xFF))
#define Blue(c) ((uint8_t)(c & 0xFF))


uint32_t Wheel(uint8_t WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return newColor(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return newColor(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return newColor(WheelPos * 3, 255 - WheelPos * 3, 0);
}




void visRainbow(uint8_t *frameBuffer, uint32_t frameBufferSize, uint32_t effectLength)
{
	uint32_t i;
	static uint8_t x = 0;

	x += 1;

	if(x == 256*5)
		x = 0;

	for( i = 0; i < frameBufferSize / 3; i++)
	{
		uint32_t color = Wheel(((i * 256) / effectLength + x) & 0xFF);

		frameBuffer[i*3 + 0] = color & 0xFF;
		frameBuffer[i*3 + 1] = color >> 8 & 0xFF;
		frameBuffer[i*3 + 2] = color >> 16 & 0xFF;
	}
}


void visDots(uint8_t *frameBuffer, uint32_t frameBufferSize, uint32_t random, uint32_t fadeOutFactor)
{
	uint32_t i;

	for( i = 0; i < frameBufferSize / 3; i++)
	{

		if(rand() % random == 0)
		{
			frameBuffer[i*3 + 0] = 255;
			frameBuffer[i*3 + 1] = 255;
			frameBuffer[i*3 + 2] = 255;
		}


		if(frameBuffer[i*3 + 0] > fadeOutFactor)
			frameBuffer[i*3 + 0] -= frameBuffer[i*3 + 0]/fadeOutFactor;
		else
			frameBuffer[i*3 + 0] = 0;

		if(frameBuffer[i*3 + 1] > fadeOutFactor)
			frameBuffer[i*3 + 1] -= frameBuffer[i*3 + 1]/fadeOutFactor;
		else
			frameBuffer[i*3 + 1] = 0;

		if(frameBuffer[i*3 + 2] > fadeOutFactor)
			frameBuffer[i*3 + 2] -= frameBuffer[i*3 + 2]/fadeOutFactor;
		else
			frameBuffer[i*3 + 2] = 0;
	}
}





void visInit()
{

	uint8_t i;

	// HELP
	// Fill the 8 structures to simulate overhead of 8 parallel strips
	// The pins are not enabled in the WS2812B init. There are enabled only PC0-3
	// The 16 channels are possible at 168MHz with 60% IRQ overhead during data TX

	// 4 parallel output LED strips needs 18% overhead during TX
	// 8 parallel output LED strips overhead is 8us of 30us period which is 28% - see the debug output PD15/13

	// If you need more parallel LED strips, increase the WS2812_BUFFER_COUNT value
	for( i = 0; i < WS2812_BUFFER_COUNT; i++)
	{

		// Set output channel/pin, GPIO_PIN_0 = 0, for GPIO_PIN_5 = 5 - this has to correspond to WS2812B_PINS
		ws2812b.item[i].channel = 1;

		// Every even output line has second frameBuffer2 with different effect
		if(i % 2 == 0)
		{
			// Your RGB framebuffer
			ws2812b.item[i].frameBufferPointer = frameBuffer;
			// RAW size of framebuffer
			ws2812b.item[i].frameBufferSize = sizeof(frameBuffer);
		} else {
			ws2812b.item[i].frameBufferPointer = frameBuffer2;
			ws2812b.item[i].frameBufferSize = sizeof(frameBuffer2);
		}

	}


	ws2812b_init();
}

uint16_t blue = 0;
uint16_t red = 0;
uint16_t green = 0;

// x is value from 0 to 11
// y is value from 0 to 15
void setLEDPixel(uint8_t x, uint8_t y, uint16_t red, uint16_t green, uint16_t blue) {
	uint32_t color = newColor(red, green, blue);

	frameBuffer[(12*x+y)*3 + 0] = color & 0xFF;
	frameBuffer[(12*x+y)*3 + 1] = color >> 8 & 0xFF;
	frameBuffer[(12*x+y)*3 + 2] = color >> 16 & 0xFF;
}

// Takes a 3D array (2D with array of color values RGB) and sets all the pixels based on this
void setAllPixelsFromGrid(uint32_t*** colorGrid) {
	uint32_t color = newColor(0, 0, 0);

	for (uint8_t x = 0; x < 12; x++) {
		for (uint8_t y = 0; y < 16; y++) {
			color = newColor(colorGrid[x][y][0], colorGrid[x][y][1], colorGrid[x][y][2]);

			frameBuffer[(12*x+y)*3 + 0] = color & 0xFF;
			frameBuffer[(12*x+y)*3 + 1] = color >> 8 & 0xFF;
			frameBuffer[(12*x+y)*3 + 2] = color >> 16 & 0xFF;
		}
	}
}

// Animate effects
void visHandle2(uint16_t *input)
{
	static uint32_t timestamp;
	static uint32_t currentTime;
	currentTime = HAL_GetTick();
	if(currentTime - timestamp > 10)
	{
		uint32_t color = 0;
		timestamp = HAL_GetTick();



		if (input[0] != 0) {
			blue = input[0];
		}
		if (input[1] != 0) {
			red = input[1];
				}
		if (input[2] != 0) {
			green = input[2];
		}

		if (blue != red || blue != green) {
			color = newColor(blue, red, green);
			for(uint32_t i = 0; i < sizeof(frameBuffer) / 3; i++) {
				frameBuffer[i*3 + 0] = color & 0xFF;
				frameBuffer[i*3 + 1] = color >> 8 & 0xFF;
				frameBuffer[i*3 + 2] = color >> 16 & 0xFF;
			}
		} else {
			visRainbow(frameBuffer, sizeof(frameBuffer), 15);
		}
		// Animate next frame, each effect into each output RGB framebuffer
		//visRainbow(frameBuffer, sizeof(frameBuffer), 15);
		//visDots(frameBuffer2, sizeof(frameBuffer2), 50, 40);
	}
}


void visHandle(uint16_t *input)
{

	if(ws2812b.transferComplete)
	{
		// Update your framebuffer here or swap buffers
		visHandle2(input);

		// Signal that buffer is changed and transfer new data
		ws2812b.startTransfer = 1;
		ws2812b_handle();
	}
}
