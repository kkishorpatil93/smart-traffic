import random
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so frontend (HTML/JS) from any laptop can communicate with this backend
CORS(app)

# Helper function to calculate green light duration based on vehicle count
def calculate_timing(vehicle_count):
    if vehicle_count > 30:
        return {"density": "High", "green_duration": 60}
    elif vehicle_count >= 10:
        return {"density": "Medium", "green_duration": 30}
    else:
        return {"density": "Low", "green_duration": 15}

# -------------------------------------------------------------------
# 1. HOME ROUTE (So visiting http://127.0.0.1:5000 shows server is online)
# -------------------------------------------------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "Smart Traffic Signal Backend is running successfully!",
        "available_endpoints": [
            "/traffic-status (GET: Simulated random traffic)",
            "/calculate?vehicles=25 (GET: Calculate time for specific vehicles)",
            "/intersection (GET: 4-way junction - North, South, East, West)",
            "/emergency?road=North (GET: Emergency override for ambulance)"
        ]
    })

# -------------------------------------------------------------------
# 2. SIMULATED RANDOM TRAFFIC (Single Road)
# -------------------------------------------------------------------
@app.route('/traffic-status', methods=['GET'])
def get_traffic_status():
    vehicle_count = random.randint(1, 50)
    timing = calculate_timing(vehicle_count)
    return jsonify({
        "vehicle_count": vehicle_count,
        "density": timing["density"],
        "green_duration": timing["green_duration"]
    })

# -------------------------------------------------------------------
# 3. CALCULATE TIMING FOR GIVEN VEHICLES (Frontend sends a number)
# -------------------------------------------------------------------
@app.route('/calculate', methods=['GET', 'POST'])
def calculate_custom():
    # Can receive vehicle count from query parameter (?vehicles=25) or JSON body
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        vehicle_count = int(data.get('vehicles', 0))
    else:
        vehicle_count = int(request.args.get('vehicles', 15))

    timing = calculate_timing(vehicle_count)
    return jsonify({
        "vehicle_count": vehicle_count,
        "density": timing["density"],
        "green_duration": timing["green_duration"]
    })

# -------------------------------------------------------------------
# 4. 4-WAY INTERSECTION (North, South, East, West)
# -------------------------------------------------------------------
@app.route('/intersection', methods=['GET'])
def get_intersection_status():
    roads = ["North", "South", "East", "West"]
    junction_data = {}

    highest_density_road = None
    max_vehicles = -1

    for road in roads:
        count = random.randint(2, 45)
        timing = calculate_timing(count)
        junction_data[road] = {
            "vehicles": count,
            "density": timing["density"],
            "suggested_green_time": timing["green_duration"]
        }
        if count > max_vehicles:
            max_vehicles = count
            highest_density_road = road

    return jsonify({
        "roads": junction_data,
        "priority_road": highest_density_road,
        "message": f"Road {highest_density_road} has the highest traffic ({max_vehicles} cars) and gets green light first."
    })

# -------------------------------------------------------------------
# 5. EMERGENCY OVERRIDE (Ambulance / Firetruck)
# -------------------------------------------------------------------
@app.route('/emergency', methods=['GET', 'POST'])
def emergency_override():
    road = request.args.get('road', 'North')
    return jsonify({
        "emergency": True,
        "priority_road": road,
        "green_duration": 60,
        "message": f"EMERGENCY! All roads set to RED. {road} road set to GREEN for emergency vehicle."
    })

# -------------------------------------------------------------------
# RUN SERVER
# -------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
