from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# In-memory node_id → api_key mapping
node_keys = {}

THINGSPEAK_URL = "https://api.thingspeak.com/update"

@app.route("/", methods=["GET"])
def home():
    return "ESP32 Base Station is Online"

@app.route("/register", methods=["POST"])
def register_node():
    data = request.json
    node_id = data.get("node_id")
    api_key = data.get("api_key")

    if not node_id or not api_key:
        return jsonify({"error": "Missing node_id or api_key"}), 400

    # Store or update mapping
    node_keys[node_id] = api_key
    print(f"Registered node: {node_id} -> {api_key}")
    return jsonify({"status": "registered"}), 200

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    node_id = data.get("node_id")
    if not node_id or node_id not in node_keys:
        return jsonify({"error": "Unregistered node_id"}), 400

    rain = data.get("rain")
    tilt = data.get("tilt")
    moisture = data.get("moisture")
    vibration = data.get("vibration")
    acceleration = data.get("acceleration")

    print(f"Data from {node_id}: Rain={rain}, Tilt={tilt}, Moisture={moisture}, Vibration={vibration}, Accel={acceleration}")

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
