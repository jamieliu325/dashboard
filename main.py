from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file
import requests
import csv
import os
import json
from db import connectTodb, read_data, LOCATION, download_data
import io


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


def get_data(api):
    try:
        response = requests.get(api)
        response.raise_for_status()
        data = response.json()["value"][0]
        water_level = round(float(data["result"]), 2)
        time = data["resultTime"].split("T")
        date = time[0]
        time = time[1].split(".")[0]
        return jsonify({
            "water_level": water_level,
            "date": date,
            "time": time
        })

    except requests.exceptions.RequestException as e:
        print("API request failed:", e)
        return jsonify({"error": "Failed to fetch water level data from API"}), 500


# get data from API and popup with marker on map
@app.route('/api_water_level/<sensor>')
def get_api_water_level(sensor):
    sensorID = LOCATION[sensor]
    api_url = f"https://api.sealevelsensors.org/v1.0/Datastreams({sensorID})/Observations?$orderby=phenomenonTime%20desc&$top=1"
    return get_data(api_url)


@app.route("/history")
def history():
    label = request.args.get('label')
    return render_template('history.html', label=label)


@app.route('/get_dates', methods=['POST'])
def get_dates():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    sensor = data.get('sensor')
    return jsonify({'redirect_url': url_for('show_table', start_date=start_date, end_date=end_date, sensor=sensor)})

# fetch data from db
@app.route('/show_table')
def show_table():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sensor = request.args.get('sensor')
    db = connectTodb()
    data = read_data(db, start_date, end_date, sensor)
    return render_template('table.html', data=data, sensor=sensor, start_date=start_date, end_date=end_date)


@app.route('/download')
def download_csv():
    sensor = request.args.get("sensor")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    db = connectTodb()
    data = download_data(db, start_date, end_date, sensor)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Time", "Sea Level (m)"])
    for row in data:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"{sensor}_data.csv"
    )


if __name__ == '__main__':
    app.run(debug=True)