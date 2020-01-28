#include <Arduino.h>
#include <Wire.h>

#include "i2c.h"

extern uint16_t currentValues[6];


void i2cInit(uint8_t address) {
    Wire.begin(address);
    Wire.onRequest(i2cRequestEvent);
}

void i2cRequestEvent() {
    for (int i = 0; i < 6; i++) {
        Wire.write(currentValues[i] & 0x00FF);
        Wire.write((currentValues[i] & 0xFF00) >> 8);
    }
}
