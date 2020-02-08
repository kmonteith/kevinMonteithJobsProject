from typing import Tuple

import requests
import json
import os
import sqlite3
from datetime import datetime
import time

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
    type TEXT Default None,
    url TEXT Default None, 
    created_at FLOAT Default 0.0, 
    company TEXT Default None, 
    company_url TEXT Default None, 
    location TEXT Default None, 
    title TEXT Default None, 
    description TEXT Default None, 
    how_to_apply TEXT Default None, 
    company_logo TEXT Default None)''')


def insert_data_to_db(cursor, data):
    for item in data:
        # datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%a %b %d %H: %M:%S ')
        timestamp = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S %Z %Y').timestamp()
        print(item['company_url'])
        cursor.execute('''INSERT OR REPLACE INTO jobs
                        (id, type, url, created_at, company, company_url, location, title, description, how_to_apply, company_logo)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                       (item['id'], item['type'], item['url'], timestamp, item['company'], item['company_url'],
                        item['location'], item['title'], item['description'], item['how_to_apply'],
                        item['company_logo']))


def jobs_to_db():
    # create db for our jobs
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    create_jobs_table(cursor)
    insert_data_to_db(cursor, get_jobs())
    close_db(conn)


def jobs_to_file():
    with open(os.path.join(ROOT_DIR, 'jobs.txt'), 'w') as f:
        f.write(json.dumps(get_jobs()))


if __name__ == '__main__':
    jobs_to_db()
