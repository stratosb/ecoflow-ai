#include "DHT.h"
#include <Arduino_RouterBridge.h>

#define DHTPIN 2     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11   // DHT 11
// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

const int sensorPin = A0;
const int dryValue = 711;
const int wetValue = 296;

unsigned long previousMillis = 0; 	// Stores last time values were updated
const long interval = 5000; 		// Every 10 seconds
int count;


void turn_led(String arg) {
  if (arg == "on") {
    digitalWrite(LED_BUILTIN, LOW);
  } else if (arg == "off") {
    digitalWrite(LED_BUILTIN, HIGH);
  }
}

void setup() {
  Serial.begin(9600);
  // initialize digital pin LED_BUILTIN as an output
  pinMode(LED_BUILTIN, OUTPUT);

  Bridge.begin();
  Bridge.provide_safe("turn_led", turn_led);
  
  dht.begin();
  // Print header
  Serial.println("temperature,humidity,moisture");
  
  count = 0;
}

void loop() { 
  unsigned long currentMillis = millis();  // Get the current time
  if (currentMillis - previousMillis >= interval) {
    count++;
    
    // Save the last time you updated the values
    previousMillis = currentMillis;

    float humidity = dht.readHumidity();
    // Read temperature as Celsius (the default)
    float temperature = dht.readTemperature();
  
    // Check if any reads failed and exit early (to try again).
    if (isnan(humidity) || isnan(temperature)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }
    //-------------
    int sensorValue = analogRead(sensorPin);
    
    int moisture = map(sensorValue,
                      dryValue,
                      wetValue,
                      0,
                      100);
    
    moisture = constrain(moisture, 0, 100);
    
    //---- Test sensor values ----
    // start with optimal state
    // temperature = 30;
    // humidity = 30;
    // moisture = 30;
    // // continue with dry state
    // if (count > 3) {
    //   temperature = 18;
    //   humidity = 80;
    //   moisture = 20;
    // }
    // if (count > 4) {
    //   temperature = 18;
    //   humidity = 80;
    //   moisture = 25;
    // }
    // if (count > 5) {
    //   temperature = 18;
    //   humidity = 80;
    //   moisture = 30;
    // }
    // if (count > 6) {
    //   temperature = 18;
    //   humidity = 80;
    //   moisture = 35;
    // }
    // if (count > 7) {
    //   temperature = 18;
    //   humidity = 80;
    //   moisture = 40;
    // }
    //------------------
  
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.print(moisture);
    Serial.println();
    
    // Format data into a simple comma-separated string
    String payload = String(temperature) + "," + String(humidity) + "," + String(moisture);

    // Call the callback of the python method
    Bridge.notify("sensor_data", payload.c_str());
  }
}
