// Arduino Code for YRL029 - IR LINE FOLLOWING SENSOR
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.        See GNU GPL v3.0.

#include <Arduino.h>

#include "i2c.h"

#define I2C_SLAVE_ADDRESS 0x58
#define STEP_TIME 1

unsigned long sensorTimerStart;

const uint8_t analogInputs[6] = {A0, A1, A2, A3, A6, A7};
const uint8_t emmitterPins[6] = {4, 5, 6, 7, 8, 9};

uint16_t currentValues[6];
 
void setup(void) {
    Serial.begin(9600);
    Serial.write("Hello World!");

    // Enable emitters
    for (int i = 0; i < 6; i++) {
            digitalWrite(emmitterPins[i], HIGH);
            pinMode(emmitterPins[i], OUTPUT); 
    }

    i2cInit(I2C_SLAVE_ADDRESS);

    sensorTimerStart = millis();
}

void loop(void) {
    static uint8_t sensorStep = 0;
    unsigned long sensorTime = millis() - sensorTimerStart;

    if (sensorTime > STEP_TIME) {
        currentValues[sensorStep] = 1023 -
                                    analogRead(analogInputs[sensorStep]);

        //Turn off current emitter
        digitalWrite(emmitterPins[sensorStep], HIGH);

        //Enable next emitter
        sensorStep = (sensorStep + 1) % 6;

        digitalWrite(emmitterPins[sensorStep], LOW);

        sensorTimerStart = millis();
    }
} 
