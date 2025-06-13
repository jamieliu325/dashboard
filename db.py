import pymysql

LOCATION = {
    "catalina" : 68,
    "burton": 262,
    "lazaretto": 74,
    "chimney": 77
}


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


def createTable(cursor, sensor):
    query = f"""
        CREATE TABLE IF NOT EXISTS `{sensor}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            time TIME NOT NULL,
            sea_level FLOAT NOT NULL,
            UNIQUE KEY unique_datetime (date, time)
        )
    """

    cursor.execute(query)

def createDB(db):
    cursor = db.cursor()

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS SeaLevelDB")
    cursor.execute("USE SeaLevelDB")

    # Create table if not exists
    for sensor in LOCATION.keys():
        createTable(cursor, sensor)

    print("Database and table are ready.")
    cursor.close()


def writeDB(db, data, sensor):
    cursor = db.cursor()
    cursor.execute("USE SeaLevelDB")

    insert_query = f"""
        INSERT INTO `{sensor}` (date, time, sea_level)
        VALUES (%s, %s, %s)
    """

    for row in data:
        date, time, sea_level = row
        try:
            cursor.execute(insert_query, (date, time, sea_level))
        except Exception as e:
            if e.args[0] == 1062:
                continue
            else:
                print(f"Failed to insert row {row}: {e}")

    db.commit()
    cursor.close()
    print("data is saved into DB")


def delete_table(db, sensor):
    cursor = db.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {sensor}")
    db.commit()


def deleteDB():

    db = connectTodb()
    cursor = db.cursor()
    # Make sure you're not using the database when dropping it
    cursor.execute("DROP DATABASE IF EXISTS SeaLevelDB")
    print("Database 'SeaLevelDB' has been deleted.")


def read_data(db, start_date, end_date, sensor):
    cursor = db.cursor()
    query = f"""
            SELECT 
                date,
                MIN(sea_level) AS min_sea_level,
                AVG(sea_level) AS avg_sea_level,
                MAX(sea_level) AS max_sea_level
            FROM `{sensor}`
            WHERE date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date ASC
        """
    cursor.execute(query, (start_date, end_date))
    return cursor.fetchall()

def download_data(db, start_date, end_date, sensor):
    cursor = db.cursor()
    query = f"""
            SELECT * FROM `{sensor}`
            WHERE date BETWEEN %s AND %s
        """
    cursor.execute(query, (start_date, end_date))
    return cursor.fetchall()

def get_date_range(db, sensor):
    cursor = db.cursor()
    cursor.execute(f"""
        SELECT CONCAT(date, ' ', time) AS datetime
        FROM `{sensor}`
        ORDER BY datetime ASC
        LIMIT 1;
    """)
    first_date = cursor.fetchone()

    cursor.execute(f"""
        SELECT CONCAT(date, ' ', time) AS datetime
        FROM `{sensor}`
        ORDER BY datetime DESC
        LIMIT 1;
    """)
    last_date = cursor.fetchone()
    return [first_date[0], last_date[0]]
