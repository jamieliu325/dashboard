import pymysql
from db import createDB, writeDB, deleteDB, connectTodb, LOCATION
import argparse
import requests
from datetime import datetime
from itertools import islice


def batched(iterable, batch_size):

    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        print("wrong date input.")
        return False


def is_valid_sensor(sensor):
    if sensor in ["burton", "chimney", "lazaretto", "catalina"]:
        return True
    return False


def main(args):
    start_date = args.start_date
    end_date = args.end_date
    sensor = args.sensor
    sensorID = LOCATION[sensor]
    api = f"https://api.sealevelsensors.org/v1.0/Datastreams({sensorID})/Observations?$filter=phenomenonTime%20ge%20{start_date}T00:00:00.000Z%20and%20phenomenonTime%20le%20{end_date}T23:59:59.000Z"

    while api:
        response = requests.get(api)
        response.raise_for_status()
        data = response.json()

        for d in data["value"]:
            resultTime = d["resultTime"].split("T")
            date = resultTime[0]
            time = resultTime[1].split(".")[0]
            sea_level = d["result"]
            yield [date, time, sea_level]
        api = data.get("@iot.nextLink")


def date_range_check(date1, date2):
    if is_valid_date(date1) and is_valid_date(date2):
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        if d2 >= d1:
            return True
        print("End date cannot be earlier than start date.")
        return False
    return False


if __name__ == "__main__":

    # deleteDB()

    parser = argparse.ArgumentParser(
        description='Provide data range to get data.')

    parser.add_argument("--sensor", type=str, required=True, help="burton, chimney, lazaretto, or catalina")
    parser.add_argument("--start_date", type=str, required=True, help="enter a start date in format xxxx-xx-xx")
    parser.add_argument("--end_date", type=str, required=True, help="enter a end date in format xxxx-xx-xx")
    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    sensor = args.sensor

    if date_range_check(start_date, end_date) and is_valid_sensor(sensor):

        db = connectTodb()

        sensor = args.sensor
        for batch in batched(main(args), 100):
            writeDB(db, batch, sensor)