from typing import Tuple

import requests
import os
import sqlite3

import time
import dateutil.parser

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


def create_jobs_table():
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
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
    conn.commit()
    conn.close()


def insert_data_to_db(data):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    try:
        cursor.execute('''INSERT OR REPLACE INTO jobs
                        (id, type, url, created_at, company, company_url, location, title, description, how_to_apply, company_logo)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                          (data['id'], data['type'], data['url'], data['created_at'], data['company'],
                           data['company_url'],
                           data['location'], data['title'], data['description'], data['how_to_apply'],
                           data['company_logo']))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


def jobs_to_db():
    # create db for our job
    create_jobs_table()
    for item in get_jobs():
        item['created_at'] = date_to_timestamp(item['created_at'])
        insert_data_to_db(item)


def date_to_timestamp(date_string):
    d = dateutil.parser.parse(date_string)
    return d.timestamp()


def jobs_to_file():
    with open(os.path.join(ROOT_DIR, 'jobs.txt'), 'w') as f:
        f.write(json.dumps(get_jobs()))


if __name__ == '__main__':
    jobs_to_db()
