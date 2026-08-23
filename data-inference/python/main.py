import time

from arduino.app_utils import App, Bridge
from edge_impulse_linux.runner import ImpulseRunner
from arduino.app_bricks.web_ui import WebUI


model_path = "/app/assets/time-series-sensor.eim"

# Initialize the Edge Impulse runner with your .eim model file
runner = ImpulseRunner(model_path)

# Verify model details
model_info = runner.init()

# Extract model labels safely
labels = model_info.get('model_parameters', {}).get('labels', [])

print(f"Model loaded successfully!")
print(f"Classification labels: {labels}")

# Edge Impulse models require a flat list of features over a time-series window.
window_features = []
REQUIRED_FEATURES_COUNT = model_info['model_parameters']['input_features_count']    # count is 3
prediction = ""

print(f"Target buffer size: {REQUIRED_FEATURES_COUNT} total sensor readings")
print("Axis count:", model_info['model_parameters'].get('axis_count'))


# method to run the inference on the real sensor values from MCU
def on_sensor_data_received(payload):
    global window_features, runner, prediction, percentage, pump_state
    
    try:
        # Parse incoming data: "temperature,humidity,moisture"
        temp, humid, moist = map(float, payload.split(','))

        print(f"values: {temp}, {humid}, {moist}")
        
        # Append the new time-step readings to our time-series array
        window_features = [temp, humid, moist]
        
        # Keep window size locked to what the model expects (slide window forward)
        if len(window_features) > REQUIRED_FEATURES_COUNT:
            window_features = window_features[-REQUIRED_FEATURES_COUNT:]

        # Once the time-series window buffer is completely full, execute inference
        if len(window_features) == REQUIRED_FEATURES_COUNT:
            res = runner.classify(window_features)
            
            if "result" in res and "classification" in res["result"]:
                # Print individual label predictions
                predictions = res["result"]["classification"]
                print(f"Predictions: {predictions}")
                
                # --- TAKE DECISIONS REAL TIME ---
                # Find the classification with the highest confidence level
                prediction = max(predictions, key=predictions.get)
                percentage = predictions[prediction]

                print(f"prediction: {prediction}")
                print(f"percentage: {percentage}")

                if prediction == "dry":
                    if percentage > 0.80:  # 90% confidence threshold
                        # Call the sketch method with the argument
                        Bridge.notify("turn_led", "on")
                        pump_state = "ON"
                    else:
                        Bridge.notify("turn_led", "off")
                        pump_state = "OFF"
                else:
                    if prediction in ["optimal", "saturated"]:
                        if percentage > 0.88:
                            Bridge.notify("turn_led", "off")
                            pump_state = "OFF"
                    
    except Exception as e:
        print(f"Error handling data packet: {e}")
        

# Register callback to call the method on_sensor_data_received
Bridge.provide("sensor_data", on_sensor_data_received)


#--- web_ui
def get_status():
    global prediction, percentage, pump_state
    result = {}
    
    if (len(window_features)) == 3:
        temp = window_features[0]
        humid = window_features[1]
        moist = window_features[2]
        outcome = prediction + "   " + f"{percentage * 100:.0f}%";
        pump_state = pump_state
        result = {"temp": temp, "humid": humid, "moist": moist, "prediction": outcome, "pump_state": pump_state}
    
    return result
    

web_ui = WebUI()
web_ui.expose_api("GET", "/api/status", get_status)
#----------


# Start the app
try:
    App.run()
finally:
    # Stop the runner cleanly only when the entire app exits
    if runner:
        runner.stop()