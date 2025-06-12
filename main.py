from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# In-memory dictionary to store node_id → api_key mapping
node_registry = {}

THINGSPEAK_URL = "https://api.thingspeak.com/update"

@app.route("/", methods=["GET"])
def home():
    return "ESP32 Base Station is Online"

@app.route("/register", methods=["POST"])
def register_node():
    """
    Registers a new node with its ThingSpeak API key.
    """
    data = request.json
    node_id = data.get("node_id")
    api_key = data.get("api_key")

    if not node_id or not api_key:
        return jsonify({"error": "Missing node_id or api_key"}), 400

    node_registry[node_id] = api_key
    print(f"[REGISTER] {node_id} -> {api_key}")
    return jsonify({"status": "registered", "node_id": node_id}), 200

@app.route("/data", methods=["POST"])
def receive_data():
    """
    Receives data from a registered node and forwards to ThingSpeak.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    node_id = data.get("node_id")
    api_key = data.get("api_key")

    if not node_id or not api_key:
        return jsonify({"error": "Missing node_id or api_key"}), 400

    # Save/update mapping every time (optional: validate once only)
    node_registry[node_id] = api_key

    # Extract sensor data
    rain = data.get("rain")
    tilt = data.get("tilt")
    moisture = data.get("moisture")
    vibration = data.get("vibration")
    acceleration = data.get("acceleration")

    print(f"\n[DATA] Node: {node_id}")
    print(f"Rain: {rain}, Tilt: {tilt}, Moisture: {moisture}, Vibration: {vibration}, Accel: {acceleration}")

    # Prepare ThingSpeak payload
    payload = {
        "api_key": api_key,
        "field1": rain,
        "field2": tilt,
        "field3": moisture,
        "field4": vibration,
        "field5": acceleration
    }

    # Send data to ThingSpeak
    response = requests.post(THINGSPEAK_URL, data=payload)

    if response.status_code == 200 and response.text != '0':
        print("[INFO] Data sent to ThingSpeak")
        return jsonify({"status": "success"}), 200
    else:
        print(f"[ERROR] Failed to send to ThingSpeak: {response.text}")
        return jsonify({"status": "fail", "reason": response.text}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
