import pymysql
from db import createDB, writeDB, delete_db, connectTodb
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

def main(args):
    start_date = args.start_date
    end_date = args.end_date
    api = f"https://api.sealevelsensors.org/v1.0/Datastreams(3)/Observations?$filter=phenomenonTime%20ge%20{start_date}T00:00:00.000Z%20and%20phenomenonTime%20le%20{end_date}T23:59:59.000Z"

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



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Provide data range to get data.')

    parser.add_argument("--start_date", type=str, required=True, help="enter a start date in format xxxx-xx-xx")
    parser.add_argument("--end_date", type=str, required=True, help="enter a end date in format xxxx-xx-xx")
    args = parser.parse_args()

    if is_valid_date(args.start_date) and is_valid_date(args.end_date):

        db = connectTodb()
        # delete_db(db)

        for batch in batched(main(args), 100):
            writeDB(db, batch)