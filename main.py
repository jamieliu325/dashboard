from flask import Flask, jsonify, send_from_directory
import csv

app = Flask(__name__)

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/water_level')
def get_water_level():
    data_path = 'data/data.csv'
    with open(data_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        first_row = next(reader, None)
        if first_row:
            water_level = round(float(first_row["water_level"]), 2)
            filtered_water_level = round(float(first_row.get("filtered_water_level", 0)), 2)
            return jsonify({
                "water_level": water_level,
                "filtered_water_level": filtered_water_level
            })
        else:
            return jsonify({"error": "No data found"}), 404

if __name__ == '__main__':
    app.run(debug=True)