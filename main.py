from flask import Flask, request, jsonify
import requests
import math

app = Flask(__name__)

# Directly include the ThingSpeak API key (avoid this in production)
THINGSPEAK_API_KEY = "HULQBZMYCXSMRSSY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

@app.route("/", methods=["GET"])
def home():
    return "ESP32 Base Station is Online"

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    rain = data.get("rain")
    tilt = data.get("tilt")
    moisture = data.get("moisture")
    vibration = data.get("vibration")
    acceleration = data.get("acceleration")

    print("Received Data:")
    print(f"Rain: {rain}, Tilt: {tilt}, Moisture: {moisture}, Vibration: {vibration}, Acceleration: {acceleration}")

    payload = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": rain,
        "field2": tilt,
        "field3": moisture,
        "field4": vibration,
        "field5": acceleration
    }

    response = requests.post(THINGSPEAK_URL, data=payload)

    if response.status_code == 200 and response.text != '0':
        print("Data sent to ThingSpeak")
        return jsonify({"status": "success"}), 200
    else:
        print(f"Failed to send to ThingSpeak: {response.text}")
        return jsonify({"status": "fail", "reason": response.text}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
