#include <Sensirion.h>

const uint8_t dataPin =  3;              // SHT serial data
const uint8_t sclkPin =  13;              // SHT serial clock
const uint8_t ledPin  = 13;              // Arduino built-in LED
const uint32_t TRHSTEP   = 5000UL;       // Sensor query period
const uint32_t BLINKSTEP =  250UL;       // LED blink period

Sensirion sht = Sensirion(dataPin, sclkPin);

uint16_t rawData;
float temperature;
float humidity;
float dewpoint;

byte ledState = 0;
byte measActive = false;
byte measType = TEMP;

unsigned long trhMillis = 0;             // Time interval tracking
unsigned long blinkMillis = 0;

void setup() {
    Serial.begin(9600);
    pinMode(ledPin, OUTPUT);
    delay(15);                           // Wait >= 11 ms before first cmd
    // Demonstrate blocking calls
    sht.measTemp(&rawData);              // sht.meas(TEMP, &rawData, BLOCK)
    temperature = sht.calcTemp(rawData);
    sht.measHumi(&rawData);              // sht.meas(HUMI, &rawData, BLOCK)
    humidity = sht.calcHumi(rawData, temperature);
    dewpoint = sht.calcDewpoint(humidity, temperature);
    logData();
}

void loop() {
    unsigned long curMillis = millis();          // Get current time

    // Rapidly blink LED.  Blocking calls take too long to allow this.
    if (curMillis - blinkMillis >= BLINKSTEP) {  // Time to toggle the LED state?
        ledState ^= 1;
        digitalWrite(ledPin, ledState);
        blinkMillis = curMillis;
    }

    // Demonstrate non-blocking calls
    if (curMillis - trhMillis >= TRHSTEP) {      // Time for new measurements?
        measActive = true;
        measType = TEMP;
        sht.meas(TEMP, &rawData, NONBLOCK);      // Start temp measurement
        trhMillis = curMillis;
    }
    if (measActive && sht.measRdy()) {           // Note: no error checking
        if (measType == TEMP) {                  // Process temp or humi?
            measType = HUMI;
            temperature = sht.calcTemp(rawData); // Convert raw sensor data
            sht.meas(HUMI, &rawData, NONBLOCK);  // Start humidity measurement
        }
        else {
            measActive = false;
            humidity = sht.calcHumi(rawData, temperature); // Convert raw sensor data
            dewpoint = sht.calcDewpoint(humidity, temperature);
            //logData();
        }
    }

    // storing incoming command
    int command;

    // is a command available?
    if (Serial.available()>0) {
        // read a key-letter
        command = Serial.read();
        switch(command) {
            case 'L':
                logDataDict();
                break;
        }
    }
}

void logDataDict() {
    Serial.print("{");
    
    Serial.print("\"temperature\":\"");
    Serial.print(temperature);
    Serial.print("\", ");

    Serial.print("\"humidity\":\"");
    Serial.print(humidity);
    Serial.print("\", ");

    Serial.print("\"dewpoint\":\"");
    Serial.print(dewpoint);
    Serial.print("\"");
    
    Serial.println("}");
}

void logData() {
    Serial.print("Temperature = ");
    Serial.print(temperature);

    Serial.print(" C, Humidity = ");
    Serial.print(humidity);

    Serial.print(" %, Dewpoint = ");
    Serial.print(dewpoint);
    Serial.println(" C");
}
