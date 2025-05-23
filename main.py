from flask import Flask, jsonify, send_from_directory
import requests
import csv

app = Flask(__name__)

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

# read data from csv and popup with marker on map
@app.route('/csv_water_level')
def get_csv_water_level():
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


# get data from API and popup with circle on map
@app.route('/api_water_level')
def get_api_water_level():
    api_url = "https://api.sealevelsensors.org/v1.0/Datastreams(3)/Observations?$filter=phenomenonTime%20ge%202019-09-19T00:00:00.000Z%20and%20phenomenonTime%20le%202019-09-20T00:00:00.000Z"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        water_level = round(float(data["value"][0]["result"]), 2)

        return jsonify({
            "water_level": water_level
        })

    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return jsonify({"error": "Failed to fetch water level data from API"}), 500

if __name__ == '__main__':
    app.run(debug=True)