import pymysql


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

def createDB(db):
    cursor = db.cursor()

    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS SeaLevelDB")
    cursor.execute("USE SeaLevelDB")

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Measurements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            time TIME NOT NULL,
            sea_level FLOAT NOT NULL,
            UNIQUE KEY unique_datetime (date, time)
        )
    """)

    print("Database and table are ready.")
    cursor.close()


def writeDB(db, data):
    cursor = db.cursor()
    cursor.execute("USE SeaLevelDB")

    insert_query = """
        INSERT INTO Measurements (date, time, sea_level)
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


def delete_db(db):
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS Measurements")
    db.commit()


def read_data(db, start_date, end_date):
    cursor = db.cursor()
    query = """
        SELECT * FROM Measurements
        WHERE date BETWEEN %s AND %s
    """
    cursor.execute(query, (start_date, end_date))
    return cursor.fetchall()
