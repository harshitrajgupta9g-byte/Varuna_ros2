#!/usr/bin/env python3
"""
Mock data server for the website dashboard demo.

Standalone Flask REST API — does NOT require ROS 2 or Gazebo running.
Serves slowly-drifting oceanographic/atmospheric readings, a drifting
position, and platform status, so the website team can build and demo
the dashboard independently of the ROS/Gazebo team's progress.

Setup:
    pip install flask flask-cors
Run:
    python3 mock_data_server.py

Endpoints:
    GET /api/sensors   -> latest oceanographic + atmospheric readings
    GET /api/position  -> latest lat/lon + heading
    GET /api/status    -> mode (autonomous/manual), battery %, comms status
"""
import random
import threading
import time

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
state_lock = threading.Lock()

sensors = {
    'water_temperature_c': -1.2,
    'salinity_psu': 34.5,
    'dissolved_oxygen_mg_l': 7.8,
    'turbidity_ntu': 2.0,
    'air_temperature_c': -8.0,
    'wind_speed_mps': 6.5,
    'barometric_pressure_hpa': 995.0,
}
drift = {
    'water_temperature_c': 0.02,
    'salinity_psu': 0.01,
    'dissolved_oxygen_mg_l': 0.03,
    'turbidity_ntu': 0.05,
    'air_temperature_c': 0.05,
    'wind_speed_mps': 0.2,
    'barometric_pressure_hpa': 0.1,
}
position = {'lat': -63.4, 'lon': -57.0, 'heading_deg': 90.0}
status = {'mode': 'autonomous', 'battery_pct': 92.0, 'comms': 'connected'}


def background_drift():
    while True:
        time.sleep(1)
        with state_lock:
            for key in sensors:
                sensors[key] = round(sensors[key] + random.uniform(-drift[key], drift[key]), 3)
            position['lat'] += random.uniform(-0.0005, 0.0005)
            position['lon'] += random.uniform(-0.0005, 0.0005)
            position['heading_deg'] = round((position['heading_deg'] + random.uniform(-3, 3)) % 360, 1)
            status['battery_pct'] = max(0.0, round(status['battery_pct'] - 0.01, 2))


@app.route('/api/sensors')
def get_sensors():
    with state_lock:
        return jsonify(dict(sensors))


@app.route('/api/position')
def get_position():
    with state_lock:
        return jsonify(dict(position))


@app.route('/api/status')
def get_status():
    with state_lock:
        return jsonify(dict(status))


if __name__ == '__main__':
    threading.Thread(target=background_drift, daemon=True).start()
    app.run(host='0.0.0.0', port=5050)
