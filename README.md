# 🚦 Smart Traffic Signal System - Backend API

A clean REST API backend built with **Python & Flask** that dynamically calculates traffic signal timings for a 4-way intersection (North, South, East, West) based on traffic density.

---

## 📁 Project Structure

```text
smart_traffic_system/
├── app.py              # Main Flask server and traffic decision logic
├── requirements.txt    # Python dependencies (Flask, Flask-CORS)
└── README.md           # API documentation and setup guide
```

---

## ⚙️ Installation & Running (Windows)

1. **Open PowerShell and navigate to the project directory:**
   ```powershell
   cd "C:\Users\TUF A15 HN007WS\smart_traffic_system"
   ```

2. **Install required libraries:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start the backend server:**
   ```powershell
   python app.py
   ```
   *The server runs at: `http://127.0.0.1:5000`*

---

## 📡 API Reference for Frontend Developer

### 1. Health Check
* **URL:** `/api/health`
* **Method:** `GET`
* **Description:** Verifies that the backend server is online and operational.
* **Response (JSON):**
  ```json
  {
    "status": "healthy",
    "service": "Smart Traffic Signal Backend",
    "version": "1.0",
    "message": "Backend is running and ready to receive traffic data."
  }
  ```

---

### 2. Traffic Signal Calculation
* **URL:** `/api/traffic`
* **Method:** `POST`
* **Header:** `Content-Type: application/json`
* **Request Body Example:**
  ```json
  {
    "north": 45,
    "south": 10,
    "east": 5,
    "west": 8
  }
  ```

* **Response Example (JSON):**
  ```json
  {
    "priority_road": "north",
    "reason": "Road 'north' has the highest vehicle count (45 vehicles).",
    "safety_rule": "Non-priority conflicting roads are strictly set to RED to prevent collisions.",
    "signal_states": {
      "north": {
        "state": "GREEN",
        "green_duration": 60,
        "yellow_duration": 3
      },
      "south": {
        "state": "RED",
        "green_duration": 0,
        "yellow_duration": 0
      },
      "east": {
        "state": "RED",
        "green_duration": 0,
        "yellow_duration": 0
      },
      "west": {
        "state": "RED",
        "green_duration": 0,
        "yellow_duration": 0
      }
    },
    "detailed_analysis": {
      "north": { "vehicle_count": 45, "density": "High", "calculated_green_duration": 60 },
      "south": { "vehicle_count": 10, "density": "Medium", "calculated_green_duration": 30 },
      "east": { "vehicle_count": 5, "density": "Low", "calculated_green_duration": 15 },
      "west": { "vehicle_count": 8, "density": "Low", "calculated_green_duration": 15 }
    }
  }
  ```

---

## 🛡️ Business Rules & Safety Logic

1. **Traffic Density Classification:**
   * **Low:** `< 10` vehicles $\rightarrow$ **15s** green time.
   * **Medium:** `10 - 30` vehicles $\rightarrow$ **30s** green time.
   * **High:** `> 30` vehicles $\rightarrow$ **60s** green time.
2. **Safe Clamping Limits:**
   * Absolute minimum green time: **10 seconds**.
   * Absolute maximum green time: **60 seconds**.
3. **Collision Prevention Safety Rule:**
   * Only the designated **priority road** receives `GREEN`.
   * All other 3 conflicting roads are strictly assigned `RED` to ensure simulated traffic cannot collide.
