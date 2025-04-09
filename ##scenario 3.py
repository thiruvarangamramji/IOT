##scenario 3

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import random

app = Flask(_name_)
def init_db():
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS traffic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            vehicle_count INTEGER,
            avg_speed REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
@app.route('/api/traffic', methods=['POST'])
def receive_traffic_data():
    data = request.json
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    c.execute("INSERT INTO traffic_data (location, vehicle_count, avg_speed, timestamp) VALUES (?, ?, ?, ?)",
              (data['location'], data['vehicle_count'], data['avg_speed'], datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Traffic data recorded"}), 201
@app.route('/api/congestion', methods=['GET'])
def get_congestion_status():
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    c.execute("SELECT location, vehicle_count, avg_speed, timestamp FROM traffic_data ORDER BY timestamp DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()

    insights = []
    for r in rows:
        congestion = "HIGH" if r[1] > 50 or r[2] < 20 else "NORMAL"
        insights.append({
            "location": r[0],
            "vehicle_count": r[1],
            "avg_speed": r[2],
            "timestamp": r[3],
            "congestion_level": congestion
        })

    return jsonify({"congestion_report": insights})
@app.route('/simulate', methods=['GET'])
def simulate_data():
    sample = {
        "location": "Master Canteen Square",
        "vehicle_count": random.randint(10, 80),
        "avg_speed": round(random.uniform(10, 40), 2)
    }
    with app.test_request_context(json=sample):
        return receive_traffic_data()

if _name_ == '_main_':
    app.run(debug=True)