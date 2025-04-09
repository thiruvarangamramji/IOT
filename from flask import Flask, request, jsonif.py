from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import random

app = Flask(_name_)

# === Database Setup ===
def init_db():
    conn = sqlite3.connect('farm_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            soil_moisture REAL,
            temperature REAL,
            humidity REAL,
            rainfall INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# === Store Sensor Data ===
@app.route('/api/sensor', methods=['POST'])
def receive_data():
    data = request.json
    conn = sqlite3.connect('farm_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO sensor_data (timestamp, soil_moisture, temperature, humidity, rainfall) VALUES (?, ?, ?, ?, ?)",
              (datetime.now(), data['soil_moisture'], data['temperature'], data['humidity'], data['rainfall']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Data stored"}), 201

# === Get Insights ===
@app.route('/api/insight', methods=['GET'])
def insights():
    conn = sqlite3.connect('farm_data.db')
    c = conn.cursor()
    c.execute("SELECT AVG(soil_moisture), AVG(temperature), AVG(humidity) FROM sensor_data")
    result = c.fetchone()
    conn.close()
    return jsonify({
        "avg_soil_moisture": round(result[0], 2),
        "avg_temperature": round(result[1], 2),
        "avg_humidity": round(result[2], 2),
        "suggest_irrigation": result[0] < 30
    })

@app.route('/simulate', methods=['GET'])
def simulate():
    sample_data = {
        "soil_moisture": random.uniform(20, 60),
        "temperature": random.uniform(24, 36),
        "humidity": random.uniform(40, 80),
        "rainfall": random.randint(0, 1)
    }
    return receive_data()

if _name_ == '_main_':
    app.run(debug=True)