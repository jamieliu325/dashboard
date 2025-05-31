from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
import csv
import os
import json
from db import connectTodb, read_data

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'tmp', 'sea_level_data')
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def serve_dashboard():
    return render_template('dashboard.html')

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


@app.route('/get_dates', methods=['POST'])
def get_dates():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    return jsonify({'redirect_url': url_for('show_table', start_date=start_date, end_date=end_date)})

@app.route('/show_table')
def show_table():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    db = connectTodb()
    data = read_data(db, start_date, end_date)
    return render_template('table.html', data=data)

# @app.route('/get_dates', methods=['POST'])
# def get_dates():
#     data = request.get_json()
#     start_date = data.get('start_date')
#     end_date = data.get('end_date')
#
#     api = f"https://api.sealevelsensors.org/v1.0/Datastreams(3)/Observations?$filter=phenomenonTime%20ge%20{start_date}T00:00:00.000Z%20and%20phenomenonTime%20le%20{end_date}T23:59:59.000Z"
#     results = []
#     while api:
#
#         response = requests.get(api)
#         response.raise_for_status()
#         data = response.json()
#
#         for d in data["value"]:
#             resultTime = d["resultTime"].split("T")
#             date = resultTime[0]
#             time = resultTime[1].split(".")[0]
#             sea_level = d["result"]
#             tmp = [date, time, sea_level]
#             results.append(tmp)
#         api = data.get("@iot.nextLink")
#
#     uid = "data_request"
#     filepath = os.path.join(DATA_DIR, f"{uid}.json")
#     with open(filepath, 'w') as f:
#         json.dump(results, f)
#
#     return jsonify({'redirect_url': url_for('show_table', data_id=uid)})
#
# @app.route('/show_table')
# def show_table():
#     data_id = request.args.get('data_id')
#     filepath = os.path.join(DATA_DIR, f"{data_id}.json")
#
#     if not os.path.exists(filepath):
#         return "Data not found", 404
#
#     with open(filepath, 'r') as f:
#         data = json.load(f)
#
#     return render_template('table.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)