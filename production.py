from typing import Tuple

import requests
import json
import os
import sqlite3

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_jobs():
    counter = 0
    jobs_json = []
    while True:
        get_url = "https://jobs.github.com/positions.json?page=" + str(counter)
        request = requests.get(get_url)
        if len(request.json()) == 0:
            break
        jobs_json.extend(request.json())
        counter = counter + 1
    return jobs_json


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def create_jobs_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS 
    jobs(id TEXT PRIMARY KEY, 
    type TEXT NOT NULL,
    url TEXT NOT NULL, 
    created_at LONG NOT NULL, 
    company TEXT NOT NULL, 
    company_url TEXT NOT NULL, 
    location TEXT NOT NULL, 
    title TEXT NOT NULL, 
    description TEXT NOT NULL, 
    how_to_apply TEXT NOT NULL, 
    company_logo TEXT NOT NULL)''')

def insert_data_to_db():
    # cursor.execute(f'''INSERT INTO STUDENTS (banner_id, first_name, last_name, gpa, credits)
    #  VALUES (1001, "John", "Santore", {random.uniform(0.0, 4.0)},
    # {random.randint(0, 120)})''')
    print("POP")


def jobs_to_db():
    # create db for our jobs
    conn, cursor = open_db("jobs.sqlite")
    print(type(conn))
    create_jobs_table(cursor)
    close_db(conn)


def jobs_to_file():
    with open(os.path.join(ROOT_DIR, 'jobs.txt'), 'w') as f:
        f.write(json.dumps(get_jobs()))


if __name__ == '__main__':
    jobs_to_db()
