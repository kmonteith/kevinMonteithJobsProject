import json

import dash
import dash_core_components as dcc
import dash_dangerously_set_inner_html
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

import production

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://fonts.googleapis.com/css?family=Lato&display=swap',
                        'https://fonts.googleapis.com/icon?family=Material+Icons']


def create_tag_html(tags):
    if tags != "null":
        tag_list = []
        for item in json.loads(tags):
            tag_list.append(
                html.P(children="#" + item['term'], className="tag"))
        return tag_list
    else:
        return "Not Available"


def create_map():
    mapbox_access_token = "pk.eyJ1Ijoia21vbnRlaXRoIiwiYSI6ImNqeGRnOXF4aDBkdmczbm1wNXM5ZDhjMG4ifQ.zPr-FTOVPZOB-CoMd-FG4w"
    fig = go.Figure()
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
            zoom=1,
            style='light'
        ),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        )
    )

    return fig


def create_gui():
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    map_fig = create_map()
    app.layout = html.Div(children=[
        html.Div(id="jobDisplay", className="jobDisplay",
                 children=[html.H1(children="Jobs Available"),
                           html.I(children="close", id="jobListClose", className="material-icons close"),
                           html.Ul(id="jobList", className="jobList")]
                 ),
        html.Nav(children=[
            html.Ul(children=[
                html.Li(children=[
                    html.H1(id="test", children='CompuJobs', className='logoName')
                ])
            ])
        ]),
        html.Div(className="content", children=[
            html.Form(id="filters", className="filters", children=[
                html.H1(className="filterHeading",
                        children=[html.I(className="material-icons", children="filter_list"), "Filter Tool"]),
                html.Label(className="filterLabels", children="Job Age"),
                dcc.RangeSlider(id="jobAge", className="jobAge",
                                min=0,
                                max=730,
                                step=1,
                                value=[0, 1080],
                                marks={
                                    90: {'label': '3 Months'},
                                    180: {'label': '6 Months'},
                                    365: {'label': '1 Year'},
                                    730: {'label': '2 Years'},
                                }
                                ),
                html.Label(className="filterLabels", children="Technologies"),
                dcc.Dropdown(
                    id="technology_filter",
                    options=production.create_tech_tag_array(production.retrieve_jobs_from_db())
                    , multi=True,
                    value=" "
                ),
                html.Label(className="filterLabels", children="Seniority Level"),
                dcc.Checklist(
                    id="seniority_filter",
                    options=[
                        {'label': 'Senior Developer', 'value': 'senior'},
                        {'label': 'Junior Developer', 'value': 'junior'}
                    ]
                ),
                html.Button("Filter", id="filterButton", type="button", className="filterButton"),
                html.Label(id="SliderOutput")
            ]),
            dcc.Graph(
                id='map',
                className='card',
                figure=map_fig,
            )])
    ])
    app.title = "CompuJobs"

    # Job Age Callback
    @app.callback(Output('map', 'figure'), [Input('filterButton', 'n_clicks')],
                  [State('jobAge', 'value'), State('technology_filter', 'value'), State('seniority_filter', 'value')])
    def display_click_data(n_clicks, job_age_value, technology_filter_value, seniority_filter_value):
        jobs_array = production.retrieve_jobs_from_db()
        jobs_array = production.filter_jobs(jobs_array, technology_filter_value, job_age_value, seniority_filter_value)
        return {
            "data": [
                {
                    "type": "scattermapbox",
                    "lat": [sub['latitude'] for sub in jobs_array],
                    "lon": [sub['longitude'] for sub in jobs_array],
                    "hovertext": [sub['location'] for sub in jobs_array],
                    "text": [sub['coord_id'] for sub in jobs_array],
                    "mode": "markers",
                    "animate": True,
                    "showlegend": False,
                    "marker": {
                        "size": 10,
                        "color": "#28aae4",
                        "opacity": 0.4
                    },
                },
            ], "layout": map_fig.layout
        }

    @app.callback(Output(component_id='jobDisplay', component_property='style'),
                  [Input('map', 'clickData'), Input('jobListClose', 'n_clicks_timestamp')])
    def show_hide_element(visibility_state, clicks):
        if visibility_state is not None or clicks is not None:
            ctx = dash.callback_context
            clicked_element = ctx.triggered[0]['prop_id'].split('.')[0]
            if clicked_element == "jobListClose":
                return {'transform': 'scale(0)'}
            elif clicked_element == "map":
                return {'transform': 'scale(1)'}

    @app.callback(Output('jobList', 'children'), [Input('map', 'clickData')],
                  [State('jobAge', 'value'), State('technology_filter', 'value'), State('seniority_filter', 'value')])
    def update_job_list(click_data, job_age_value, technology_filter_value, seniority_filter_value):
        if click_data is not None:
            coord_id = click_data.get('points')[0].get('text')
            jobs_array = production.retrieve_jobs_from_db()
            jobs_array = production.filter_jobs(jobs_array, technology_filter_value, job_age_value,
                                                seniority_filter_value)
            jobs_array = production.get_jobs_from_coord_id(jobs_array, coord_id)
            list_jobs = []

            for item in jobs_array:
                list_jobs.append(html.Li(
                    children=[html.H4(className='jobTitle', children=item['title']),
                              html.H5(children='Tags: ', className='label'),
                              html.Div(children=create_tag_html(item['tags'])),
                              html.H5(children='Link: ', className='label'),
                              html.P(children=item['company_url']),
                              html.H5(children='Description: ', className='label'),
                              html.P([dash_dangerously_set_inner_html.DangerouslySetInnerHTML(item['description'])]),
                              ]))
            return list_jobs

    app.run_server(debug=False)
