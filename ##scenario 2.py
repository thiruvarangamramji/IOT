##scenario 2

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import random

app = Flask(_name_)


def init_db():
    conn = sqlite3.connect('bins.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bin_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id TEXT,
            location TEXT,
            fill_level INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


@app.route('/api/bin', methods=['POST'])
def update_bin_status():
    data = request.json
    bin_id = data['bin_id']
    location = data['location']
    fill_level = data['fill_level']

    conn = sqlite3.connect('bins.db')
    c = conn.cursor()
    c.execute("INSERT INTO bin_data (bin_id, location, fill_level, timestamp) VALUES (?, ?, ?, ?)",
              (bin_id, location, fill_level, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Bin data stored"}), 201


@app.route('/api/alerts', methods=['GET'])
def get_full_bins():
    conn = sqlite3.connect('bins.db')
    c = conn.cursor()
    c.execute("SELECT bin_id, location, fill_level, timestamp FROM bin_data WHERE fill_level >= 80 ORDER BY timestamp DESC")
    results = c.fetchall()
    conn.close()

    bins = []
    for row in results:
        bins.append({
            "bin_id": row[0],
            "location": row[1],
            "fill_level": row[2],
            "timestamp": row[3]
        })

    return jsonify({"alert_bins": bins})

@app.route('/simulate', methods=['GET'])
def simulate_data():
    sample_data = {
        "bin_id": f"BIN-{random.randint(1, 5)}",
        "location": "Ward-12, BBSR",
        "fill_level": random.randint(10, 100)
    }
    with app.test_request_context(json=sample_data):
        return update_bin_status()

if _name_ == '_main_':
    app.run(debug=True)