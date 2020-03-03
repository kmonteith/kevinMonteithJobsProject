import json
from threading import Timer
from typing import Tuple
import requests
import os
import sqlite3
import dateutil.parser
import feedparser
import plotly.graph_objs as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import webbrowser
from dash.dependencies import Input, Output
from geopy import geocoders
from geopy.exc import GeocoderTimedOut
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def do_click(trace, points, state):
    print(trace)




def create_map():
    mapbox_access_token = "pk.eyJ1Ijoia21vbnRlaXRoIiwiYSI6ImNqeGRnOXF4aDBkdmczbm1wNXM5ZDhjMG4ifQ.zPr-FTOVPZOB-CoMd-FG4w"
    df = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/Nuclear%20Waste%20Sites%20'
        'on%20American%20Campuses.csv')
    site_lat = df.lat
    site_lon = df.lon
    locations_name = df.text
    fig = go.Figure()
    jobs_array = retrieve_jobs_from_db()
    scatter_map = fig.add_trace(go.Scattermapbox(
        lat=[ sub['latitude'] for sub in jobs_array ] ,
        lon=[ sub['longitude'] for sub in jobs_array ] ,
        hovertext=[ sub['location'] for sub in jobs_array ],
        text=[ sub['id'] for sub in jobs_array ],
        mode='markers',
        textfont=dict(
            family='sans serif',
            size=200,
            color='#ff7f0e'
        ),
        marker=go.scattermapbox.Marker(
            size=10,
            color='rgb(255, 0, 0)',
            opacity=0.4
        ),
        hoverinfo='text',

    ))
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=38,
                lon=-94
            ),
            pitch=0,
            zoom=3,
            style='light'
        ),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        height=600,
        width=1200
    )

    return fig


def create_gui():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    map_fig = create_map()
    app.layout = html.Div(children=[
        html.Nav(children=[
            html.Ul(children=[
                html.Li(children=[
                    html.H1(id="test", children='CompuJobs', className='logoName')
                ])
            ])
        ]),
        html.Form(id="test2",children=[
            dcc.Input(placeholder="Query", type="text", id="filter")

        ]),
        dcc.Graph(
            id='map',
            className='card',
            figure=map_fig,
        )
    ])
    app.title = "D";

    @app.callback(
        Output('test2', 'children'),
        [Input('map', 'clickData')])
    def display_click_data(clickData):
        return json.dumps(clickData, indent=2)



    app.run_server(debug=False)


def retrieve_jobs_from_db():
    conn = sqlite3.connect(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    result = cursor.execute('''SELECT * FROM `jobs`''')
    job_array = result.fetchall()
    close_db(conn)
    return job_array


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
    return hacker_rank_jobs_json


def get_stack_overflow_jobs():
    stack_overflow_jobs = []
    temp_entry = {}
    d = feedparser.parse("https://stackoverflow.com/jobs/feed")
    for item in d.get('entries'):
        temp_entry = {'title': item.get('title'), 'id': item.get('id'), 'url': item.get('link'),
                      'created_at': item.get('published'), 'company': item.get('authors')[0].get('name'),
                      'company_url': 'Not Available', 'location': item.get('location'),
                      'how_to_apply': 'Refer to description', 'description': item.get('summary'),
                      'company_logo': "Not Available", 'type': 'Not Available'}
        stack_overflow_jobs.append(temp_entry)
        temp_entry = {}
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
    type TEXT Default None,
    url TEXT Default None,
    created_at FLOAT Default 0.0,
    company TEXT Default None,
    company_url TEXT Default None,
    location TEXT Default None,
    title TEXT Default None,
    description TEXT Default None,
    how_to_apply TEXT Default None,
    company_logo TEXT Default None,
    longitude FLOAT Default NULL,
    latitude FLOAT Default NULL)''')
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
        result = cursor.execute("SELECT `longitude`,`latitude` FROM `coordinates` WHERE `location` = '"+location+"'")
        query_result = result.fetchone()
        close_db(conn)
        return query_result['longitude'], query_result['latitude']
    else:
        gn = geocoders.Nominatim(user_agent="Jobs_Project")
        if gn.geocode(location) is not None:
            try:
                coordinates = gn.geocode(location, timeout=5)
                insert_into_location_cache(location,coordinates.longitude,coordinates.latitude)
                return coordinates.longitude, coordinates.latitude
            except GeocoderTimedOut:
                time.sleep(1)
                return get_coordinates_from_location(location)
        else:
            return "NULL","NULL"


def insert_into_location_cache(location,lon,lat):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'coordinates.sqlite'))
    try:
        cursor.execute('''INSERT OR REPLACE INTO coordinates (location, longitude, latitude) VALUES (?,?,?)''',
                       (location, lon, lat))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        conn.close()
        return False


def check_coordinate_cache(location):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'coordinates.sqlite'))
    result = cursor.execute("SELECT `id` FROM `coordinates` WHERE `location` = '"+location+"'")
    if len(result.fetchall()) > 0:
        close_db(conn)
        return True
    close_db(conn)
    return False


def parse_location(location):
    if location is not None:
        location = location.replace('remote', ' ')
        location = location.replace('Remote', ' ')
        location = location.replace('(', ' ')
        location = location.replace(')', ' ')
    return location


def insert_data_to_db(data):
    conn, cursor = open_db(os.path.join(ROOT_DIR, 'jobs.sqlite'))
    try:
        location = parse_location(data['location'])
        lon, lat = get_coordinates_from_location(location)
        cursor.execute('''INSERT OR REPLACE INTO jobs
                        (id, type, url, created_at, company, company_url, location, title, description, how_to_apply,
                        company_logo,longitude,latitude)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (data['id'], data['type'], data['url'], data['created_at'], data['company'],
                        data['company_url'],
                        str(location), data['title'], data['description'], data['how_to_apply'],
                        data['company_logo'],lon,lat))

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
    counter = 0;
    for item in jobs_array:
        item['created_at'] = date_to_timestamp(item['created_at'])
        insert_data_to_db(item)
        percentage = (counter/jobs_array_length)*100
        print(str(percentage)+"% done")
        counter = counter+1


def date_to_timestamp(date_string):
    d = dateutil.parser.parse(date_string)
    return d.timestamp()


def jobs_to_file():
    with open(os.path.join(ROOT_DIR, 'jobs.txt'), 'w') as f:
        f.write(json.dumps(get_jobs()))


if __name__ == '__main__':
    # jobs_to_db()
    #create_jobs_table()
    #create_coordinate_table()
    #jobs_to_db()
    # retrieve_jobs_from_db()
    # Timer(2, open_browser).start();
    create_gui()
