import pymysql
from db import createDB, writeDB
import argparse
import requests


def connectTodb():
    # connect with mysql, start mysql first
    DB_HOST = 'localhost'
    DB_USER = 'root'
    # Please set your root password to below or replace it with your own password
    DB_PASSWORD = 'omscs2023'
    # Connect to MySQL database
    db = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    # create user, database, tables
    createDB(db)
    return db

def main(db, args):
    start_date = args.start_date
    end_date = args.end_date
    api = f"https://api.sealevelsensors.org/v1.0/Datastreams(3)/Observations?$filter=phenomenonTime%20ge%20{start_date}T00:00:00.000Z%20and%20phenomenonTime%20le%20{end_date}T23:59:59.000Z"
    results = []
    while api:
        response = requests.get(api)
        response.raise_for_status()
        data = response.json()

        for d in data["value"]:
            resultTime = d["resultTime"].split("T")
            date = resultTime[0]
            time = resultTime[1].split(".")[0]
            sea_level = d["result"]
            tmp = [date, time, sea_level]
            results.append(tmp)
        api = data.get("@iot.nextLink")
    print("data is fetched from API.")
    writeDB(db, results)

if __name__ == "__main__":


    # python load_data.py \
    #     --start_date 2019-09-18 \
    #     --end_date 2019-09-20

    parser = argparse.ArgumentParser(
        description='Provide data range to get data.')

    parser.add_argument("--start_date", type=str, required=True, help="enter a start date in format xxxx-xx-xx")
    parser.add_argument("--end_date", type=str, required=True, help="enter a end date in format xxxx-xx-xx")
    args = parser.parse_args()


    db = connectTodb()
    main(db, args)