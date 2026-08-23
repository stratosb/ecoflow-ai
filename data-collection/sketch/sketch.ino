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
const long interval = 10000; 		// Every 10 seconds


void setup() {
  Bridge.begin();
  Serial.begin(9600);
  
  dht.begin();
  // Print header
  Serial.println("temperature,humidity,moisture");
}

void loop() {
  unsigned long currentMillis = millis();  // Get the current time
  if (currentMillis - previousMillis >= interval) {
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

    //Serial.print("Moisture: ");
    //Serial.println(sensorValue);
    
    int moisture = map(sensorValue,
                      dryValue,
                      wetValue,
                      0,
                      100);
  
    moisture = constrain(moisture, 0, 100);
  
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.print(moisture);
    Serial.println();

    Bridge.notify("record_sensor_samples", temperature, humidity, moisture);
  }
}
