import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# =====================================================================
# 1. APPLICATION CONFIGURATION
# =====================================================================
app = Flask(__name__)

# Configurable CORS: Allows your friend's frontend to connect.
# "*" means any frontend origin can connect. You can also specify an exact URL.
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGIN}})

# Configurable Traffic Timing Settings (in seconds)
MIN_GREEN_TIME = 10   # Absolute safe minimum green time
MAX_GREEN_TIME = 60   # Absolute safe maximum green time
YELLOW_TIME = 3       # Safe yellow transition time

# Density Thresholds (number of vehicles)
LOW_THRESHOLD = 10    # Less than 10 vehicles = Low
HIGH_THRESHOLD = 30   # More than 30 vehicles = High

# Default durations per density category
DURATION_LOW = 15     # Low traffic gets 15s
DURATION_MEDIUM = 30  # Medium traffic gets 30s
DURATION_HIGH = 60    # High traffic gets 60s


# =====================================================================
# 2. HELPER FUNCTIONS (The Brain)
# =====================================================================

def classify_density(count: int) -> str:
    """Classifies vehicle count into Low, Medium, or High."""
    if count > HIGH_THRESHOLD:
        return "High"
    elif count >= LOW_THRESHOLD:
        return "Medium"
    else:
        return "Low"


def calculate_green_duration(density: str) -> int:
    """
    Calculates green light duration based on density,
    safely clamped between MIN_GREEN_TIME and MAX_GREEN_TIME.
    """
    if density == "High":
        raw_duration = DURATION_HIGH
    elif density == "Medium":
        raw_duration = DURATION_MEDIUM
    else:
        raw_duration = DURATION_LOW

    # Enforce safe minimum and maximum limits
    safe_duration = max(MIN_GREEN_TIME, min(raw_duration, MAX_GREEN_TIME))
    return safe_duration


# =====================================================================
# 3. API ENDPOINTS
# =====================================================================

@app.route('/', methods=['GET'])
def home():
    """Serves the interactive frontend dashboard if available, else JSON status."""
    if os.path.exists('index.html'):
        return send_file('index.html')
    return jsonify({
        "status": "online",
        "service": "Smart Traffic Signal Backend",
        "endpoints": {
            "health": "/api/health",
            "traffic": "/api/traffic"
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint 1: Health check to verify backend status.
    Method: GET
    """
    return jsonify({
        "status": "healthy",
        "service": "Smart Traffic Signal Backend",
        "version": "1.0",
        "message": "Backend is running and ready to receive traffic data."
    }), 200


@app.route('/api/traffic', methods=['GET', 'POST'])
def calculate_traffic_plan():
    """
    Endpoint 2: Receives vehicle counts for North, South, East, West.
    - POST: Receives real counts from frontend JSON body.
    - GET: Returns a sample calculated plan (convenient for browser testing).
    """
    required_roads = ["north", "south", "east", "west"]

    # If accessed directly in browser (GET request), use sample traffic data
    if request.method == 'GET':
        data = {
            "north": int(request.args.get('north', 25)),
            "south": int(request.args.get('south', 10)),
            "east": int(request.args.get('east', 45)),
            "west": int(request.args.get('west', 12))
        }
    else:
        # POST request from frontend
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "error": "Invalid request. Please send a JSON body."
            }), 400

        # Validate all 4 required roads
        for road in required_roads:
            if road not in data:
                return jsonify({
                    "error": f"Missing required road: '{road}'. Please provide vehicle counts for north, south, east, and west."
                }), 400
            if not isinstance(data[road], int) or data[road] < 0:
                return jsonify({
                    "error": f"Invalid vehicle count for '{road}'. Must be a non-negative whole number."
                }), 400

    # 3. Analyze each road
    analysis = {}
    highest_count = -1
    priority_road = None

    for road in required_roads:
        count = data[road]
        density = classify_density(count)
        duration = calculate_green_duration(density)

        analysis[road] = {
            "vehicle_count": count,
            "density": density,
            "calculated_green_duration": duration
        }

        # Select road with the highest traffic for green priority
        if count > highest_count:
            highest_count = count
            priority_road = road

    # 4. SAFETY RULE: Collision Prevention
    # Conflicting roads must NEVER be green at the same time.
    # ONLY the priority road gets GREEN. All other 3 conflicting roads are set to RED.
    signal_states = {}
    for road in required_roads:
        if road == priority_road:
            signal_states[road] = {
                "state": "GREEN",
                "green_duration": analysis[road]["calculated_green_duration"],
                "yellow_duration": YELLOW_TIME
            }
        else:
            signal_states[road] = {
                "state": "RED",
                "green_duration": 0,
                "yellow_duration": 0
            }

    # 5. Return complete signal plan
    response_payload = {
        "priority_road": priority_road,
        "reason": f"Road '{priority_road}' has the highest vehicle count ({highest_count} vehicles).",
        "safety_rule": "Non-priority conflicting roads are strictly set to RED to prevent collisions.",
        "signal_states": signal_states,
        "detailed_analysis": analysis
    }

    return jsonify(response_payload), 200


# =====================================================================
# 4. START THE SERVER
# =====================================================================
if __name__ == '__main__':
    # Runs the Flask development server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
