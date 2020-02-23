from threading import Timer
from typing import Tuple
import requests
import os
import sqlite3
import dateutil.parser
import feedparser
import plotly.graph_objects as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import webbrowser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_map():
    mapbox_access_token = "pk.eyJ1Ijoia21vbnRlaXRoIiwiYSI6ImNqeGRnOXF4aDBkdmczbm1wNXM5ZDhjMG4ifQ.zPr-FTOVPZOB-CoMd-FG4w"
    df = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/Nuclear%20Waste%20Sites%20on%20American%20Campuses.csv')
    site_lat = df.lat
    site_lon = df.lon
    locations_name = df.text

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=site_lat,
        lon=site_lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=17,
            color='rgb(255, 0, 0)',
            opacity=0.7
        ),
        text=locations_name,
        hoverinfo='text'
    ))

    fig.add_trace(go.Scattermapbox(
        lat=site_lat,
        lon=site_lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
            color='rgb(242, 177, 172)',
            opacity=0.7
        ),
        hoverinfo='none'
    ))

    fig.update_layout(
        title='Nuclear Waste Sites on Campus',
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
    )

    return fig



def create_gui():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        html.H1(children='CompuJobs'),
        dcc.Graph(
            id='example-graph',
            figure=create_map()
        )
    ])
    app.title = "D";
    app.run_server(debug=False)

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
                        (id, type, url, created_at, company, company_url, location, title, description, how_to_apply,
                        company_logo)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                       (data['id'], data['type'], data['url'], data['created_at'], data['company'],
                        data['company_url'],
                        data['location'], data['title'], data['description'], data['how_to_apply'],
                        data['company_logo']))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
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


# def jobs_to_file():
#    with open(os.path.join(ROOT_DIR, 'jobs.txt'), 'w') as f:
#        f.write(json.dumps(get_jobs()))


if __name__ == '__main__':
    #jobs_to_db()
    Timer(2, open_browser).start();
    create_gui()

