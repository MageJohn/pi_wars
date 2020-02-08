// Arduino Code for YRL029 - IR LINE FOLLOWING SENSOR
//
// Copyright (C) 2019 James Hilder, York Robotics Laboratory
// This is free software, with no warranty, and you are welcome to redistribute it
// under certain conditions.        See GNU GPL v3.0.

#include <Arduino.h>
#include <Wire.h>

#define I2C_SLAVE_ADDRESS (0x58)
#define STEP_TIME (1000)
#define N_SENSORS (4)

unsigned long sensorTimerStart;

const uint8_t analogInputs[] = {A0, A2, A3, A7};
const uint8_t emmitterPins[] = {4, 6, 7, 9};

union Values {
    uint16_t combined[N_SENSORS];
    uint8_t low_high[N_SENSORS * 2];
};

union Values currentValues;


void i2cRequestEvent() {
    Wire.write(currentValues.low_high, N_SENSORS * 2);
}

void setup(void) {
    Serial.begin(9600);
    Serial.write("Hello World!");

    // Enable emitters
    for (int i = 0; i < N_SENSORS; i++) {
            digitalWrite(emmitterPins[i], HIGH);
            pinMode(emmitterPins[i], OUTPUT);
    }

    Wire.begin(I2C_SLAVE_ADDRESS);
    Wire.onRequest(i2cRequestEvent);

    sensorTimerStart = micros();
}

void loop(void) {
    static uint8_t sensorStep = 0;
    unsigned long sensorTime = micros() - sensorTimerStart;

    if (sensorTime > STEP_TIME) {
        currentValues.combined[sensorStep] = 1023 -
                                    analogRead(analogInputs[sensorStep]);

        //Turn off current emitter
        digitalWrite(emmitterPins[sensorStep], HIGH);

        //Enable next emitter
        sensorStep = (sensorStep + 1) % N_SENSORS;

        digitalWrite(emmitterPins[sensorStep], LOW);

        sensorTimerStart = micros();
    }
}
