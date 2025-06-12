from flask import Flask, request, jsonify
import requests
import math

app = Flask(__name__)

# In-memory storage for node_id to API key mapping
node_keys = {
    "node1": "HULQBZMYCXSMRSSY"  # Pre-mapped for testing
    # Add more node IDs and their API keys here
}

THINGSPEAK_URL = "https://api.thingspeak.com/update"

@app.route("/", methods=["GET"])
def home():
    return "ESP32 Base Station is Online"

@app.route("/register", methods=["POST"])
def register_node():
    data = request.json
    node_id = data.get("node_id")

    if not node_id:
        return jsonify({"error": "Missing node_id"}), 400

    # Assign API key (hardcoded for now or dynamically assign)
    if node_id not in node_keys:
        return jsonify({"error": "Unknown node_id. Add it to server config."}), 400

    api_key = node_keys[node_id]
    return jsonify({"status": "registered", "api_key": api_key}), 200

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    node_id = data.get("node_id")
    if not node_id or node_id not in node_keys:
        return jsonify({"error": "Invalid or unregistered node_id"}), 400

    rain = data.get("rain")
    tilt = data.get("tilt")
    moisture = data.get("moisture")
    vibration = data.get("vibration")
    acceleration = data.get("acceleration")

    print(f"Node {node_id} Sent Data:")
    print(f"Rain: {rain}, Tilt: {tilt}, Moisture: {moisture}, Vibration: {vibration}, Acceleration: {acceleration}")

    payload = {
        "api_key": node_keys[node_id],
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
