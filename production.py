import json
from threading import Timer
from typing import Tuple
import requests
import os
import sqlite3
import dateutil.parser
import feedparser
import webbrowser
from geopy import geocoders
from geopy.exc import GeocoderTimedOut
import time
import gui

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def retrieve_jobs_from_db():
    conn = sqlite3.connect(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    result = cursor.execute('''SELECT * FROM `jobs`''')
    job_array = result.fetchall()
    close_db(conn)
    return job_array


def filter_jobs(jobs_array, technology_filter_value=None, job_age_value=None,
                seniority_filter_value=""):
    if job_age_value is None:
        job_age_value = [0, 730]
    if technology_filter_value is None:
        technology_filter_value = [""]
    jobs_array = filter_map_technology(jobs_array, technology_filter_value)
    jobs_array = filter_map_age(jobs_array, job_age_value[0], job_age_value[1])
    jobs_array = filter_map_seniority(jobs_array, seniority_filter_value)
    return jobs_array


def create_tech_tag_array(job_array):
    term_array = []
    terms = []
    for i in job_array:
        temp = json.loads(i['tags'])
        if temp is not None:
            for j in temp:
                if j['term'] not in terms:
                    terms.append(j['term'])
                    term_array.append({'label': j['term'], 'value': j['term']})
    return term_array


def filter_map_age(jobs_array, start_age, end_age):
    filtered_jobs = []
    current_time = time.time()
    filter_time_end = current_time - (start_age * 86400)
    filter_time_begin = current_time - (end_age * 86400)
    for item in jobs_array:
        if filter_time_end > item['created_at'] > filter_time_begin:
            filtered_jobs.append(item)
    return filtered_jobs


def filter_map_technology(jobs_array, keywords):
    filtered_jobs = []
    for item in jobs_array:
        tag_array = json.loads(item['tags'])
        if all(substring in item['description'] for substring in keywords) or all(
                substring in item['title'] for substring in keywords):
            filtered_jobs.append(item)
        else:
            if tag_array is not None:
                counter = 0
                for i in keywords:
                    if any(d['term'] == i for d in tag_array):
                        counter = counter + 1
                if counter == len(keywords):
                    filtered_jobs.append(item)
    return filtered_jobs


def filter_map_seniority(jobs_array, seniority):
    filtered_jobs = []
    if seniority is not None:
        for item in jobs_array:
            if all(substring in item['description'] for substring in seniority) or all(
                    substring in item['title'] for substring in seniority):
                filtered_jobs.append(item)
    else:
        filtered_jobs = jobs_array
    return filtered_jobs


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')


def get_jobs():
    jobs_json = get_hacker_rank_jobs() + get_stack_overflow_jobs()
    return jobs_json


def get_hacker_rank_jobs():
    counter = 0
    hacker_rank_jobs_json = []
    while True:
        get_url = "https://jobs.github.com/positions.json?page=" + str(counter)
        request = requests.get(get_url)
        if request is None:
            break
        if len(request.json()) == 0:
            break
        hacker_rank_jobs_json.extend(request.json())
        counter = counter + 1
    # print(hacker_rank_jobs_json[0])
    return hacker_rank_jobs_json


def get_stack_overflow_jobs():
    stack_overflow_jobs = []
    d = feedparser.parse("https://stackoverflow.com/jobs/feed")
    for item in d.get('entries'):
        temp_entry = {'title': item.get('title'), 'id': item.get('id'), 'url': item.get('link'),
                      'created_at': item.get('published'), 'company': item.get('authors')[0].get('name'),
                      'company_url': 'Not Available', 'location': item.get('location'),
                      'how_to_apply': 'Refer to description', 'description': item.get('summary'),
                      'company_logo': "Not Available", 'type': 'Not Available', 'tags': item.get('tags')}
        stack_overflow_jobs.append(temp_entry)
    return stack_overflow_jobs


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def create_jobs_table():
    drop_table()
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    cursor.execute('''CREATE TABLE IF NOT EXISTS
    jobs(id TEXT PRIMARY KEY,
    type TEXT Default NULL,
    url TEXT Default NULL,
    created_at FLOAT Default 0.0,
    company TEXT Default NULL,
    company_url TEXT Default NULL,
    location TEXT Default NULL,
    title TEXT Default NULL,
    description TEXT Default NULL,
    how_to_apply TEXT Default NULL,
    company_logo TEXT Default NULL,
    tags TEXT Default NULL,
    longitude FLOAT Default NULL,
    latitude FLOAT Default NULL,
    coord_id INT DEFAULT NULL)''')
    conn.commit()
    conn.close()


def create_coordinate_table():
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'coordinates.sqlite'))
    cursor.execute('''DROP TABLE coordinates''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS
    coordinates(id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT Default NULL,
    longitude FLOAT Default NULL,
    latitude FLOAT Default NULL)''')
    conn.commit()
    conn.close()


def drop_table():
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    cursor.execute('''DROP TABLE `jobs`''')
    conn.commit()
    conn.close()


def get_coordinates_from_location(location):
    if location is not None and check_coordinate_cache(location):
        conn = sqlite3.connect(os.path.join(ROOT_DIR, 'coordinates.sqlite'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT `longitude`,`latitude`,`id` FROM `coordinates` WHERE `location` = '" + location + "'")
        query_result = result.fetchone()
        close_db(conn)
        return query_result['longitude'], query_result['latitude'], query_result['id']
    else:
        gn = geocoders.Nominatim(user_agent="Jobs_Project_kmonteith_rand")
        try:
            time.sleep(1.5)
            location_geocode = gn.geocode(location, timeout=1000)
            if location_geocode is not None:
                coordinates = location_geocode
                result, coord_id = insert_into_location_cache(location, coordinates.longitude, coordinates.latitude)
                return coordinates.longitude, coordinates.latitude, coord_id
            else:
                return "NULL", "NULL", -1
        except GeocoderTimedOut:
            time.sleep(1)
            return get_coordinates_from_location(location)


def insert_into_location_cache(location, lon, lat):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'coordinates.sqlite'))
    try:
        cursor.execute('''INSERT OR REPLACE INTO coordinates (location, longitude, latitude) VALUES (?,?,?)''',
                       (location, lon, lat))
        conn.commit()
        conn.close()
        return True, cursor.lastrowid
    except sqlite3.Error as e:
        print(e)
        conn.close()
        return False


def check_coordinate_cache(location):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'coordinates.sqlite'))
    result = cursor.execute("SELECT `id` FROM `coordinates` WHERE `location` = '" + location + "'")
    if len(result.fetchall()) > 0:
        close_db(conn)
        return True
    close_db(conn)
    return False


def parse_location(location):
    if location is not None:
        location = location.replace('remote', ' ')
        location = location.replace('Remote', ' ')
        location = location.replace('CA', 'California ')
        location = location.replace('(', ' ')
        location = location.replace(')', ' ')
    return location


def insert_data_to_db(data):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    try:
        location = parse_location(data['location'])
        lon, lat, coord_id = get_coordinates_from_location(location)
        cursor.execute('''INSERT OR REPLACE INTO jobs
                        (id, type, url, created_at, company, company_url, location, title, description, how_to_apply,
                        company_logo,longitude,latitude,tags,coord_id)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (data['id'], data['type'], data['url'], data['created_at'], data['company'],
                        data['company_url'],
                        str(location), data['title'], data['description'], data['how_to_apply'],
                        data['company_logo'], lon, lat, json.dumps(data.get('tags')), coord_id))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        conn.close()
        print(e)
        return False


def jobs_to_db():
    # create db for our job
    create_jobs_table()
    jobs_array = get_jobs()
    jobs_array_length = len(jobs_array)
    counter = 0
    for item in jobs_array:
        item['created_at'] = date_to_timestamp(item['created_at'])
        insert_data_to_db(item)
        percentage = (counter / jobs_array_length) * 100
        print(str(percentage) + "% done")
        counter = counter + 1


def get_jobs_from_coord_id(jobs_array, coord_id):
    filtered_array = []
    for item in jobs_array:
        if item['coord_id'] == coord_id:
            filtered_array.append(item)
    return filtered_array


def date_to_timestamp(date_string):
    d = dateutil.parser.parse(date_string)
    return d.timestamp()


def jobs_to_file():
    with open(os.path.join(ROOT_DIR, 'jobs.txt'), 'w') as f:
        f.write(json.dumps(get_jobs()))


if __name__ == '__main__':
    Timer(2, open_browser).start();
    gui.create_gui()
