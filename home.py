import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State, ALL, MATCH
# import Pages.marine, Pages.offshore, Pages.lookup, Pages.drilldown, Pages.configure, Pages.start, Pages.removal
from bike_app import app, server, asts
from google_places_api import query_gp
import numpy as np
import os

public_token = 'pk.eyJ1IjoiZGNoaXF1ZTMiLCJhIjoiY2tmdmg5Y2FjMTFmbzJzczMwcnRhMG50bCJ9.JgdIR-3Nkxb2hRc-5UQ79w'


def colorselector(num_of_bikes, val):
    if num_of_bikes < val: 
        color = 'rgb(255,0,0)' # Red for not available
        #color = 'rgb(0,255,0)'
    elif num_of_bikes - 2 < val:
        color = 'rgb(255,255,0)' # Yellow for available but close
        #color = 'rgb(0,255,0)'
    elif num_of_bikes > val:
        color = 'rgb(0,255,0)' # Green for available
    return color

def filter_by_radius(df, pos, r):
    R = 6371e3 # Meters
    phi1 = pos['lat']*np.pi/180
    phi2 = df.loc[:,'_lat']*np.pi/180
    dphi = (df.loc[:,'_lat'] - pos['lat'])*np.pi/180
    dlamb = (df.loc[:,'_long'] - pos['long'])*np.pi/180
    a = np.sin(dphi/2) * np.sin(dphi/2) + np.cos(phi1)*np.cos(phi2)*np.sin(dlamb/2)*np.sin(dlamb/2)
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))

    d = R * c # in meters
    return df.loc[d <= r,'dock_id']

def draw_circle(r):
    x = []
    y = []
    for d in range(0,361,1):
        x += [r*np.sin(d)]
        y += [r*np.cos(d)]
    return np.array(x), np.array(y)

def convert_circle_to_latlon(pos, r):
    R = 6371e3
    x, y = draw_circle(r)
    lons = pos['long'] + (x*180)/(R*np.pi*np.cos(pos['lat']*np.pi/180))
    lats = pos['lat'] + (y*180)/(R*np.pi)
    return lats, lons


app.layout = html.Div(
    [
        html.Div(id="side-bar-div", children=asts.sidebar(), className="side-bar"),
        dcc.Location(id="url", refresh=False),
        # html.Div(id="nav-bar-div", children=asts.navbar(), style={'width':'22%'}),
        html.Div(id="page-content", style={"display": "flex",
                                           "flex-flow": "column",
                                           "height": "100%",
                                           "flex": "1 1 auto"}),
    ], style={"display": "flex",
              "flex-flow": "row",
              "height": "100%"}
)

landing_modal = dbc.Modal(
    [
        dbc.ModalHeader("Welcome to BikeCast for NYC!", style={'justify-content': 'center'}),
        dbc.ModalBody([
            html.Div("You can use BikeCast to browse through citibike statikons in NYC."),
            html.Div("This visualization assumes today is August 24th, 2020"),
            html.Div("In the left sidebar, you can select a time+hour and party size to see predicted availability at a future time! (7 days ahead)"),
            html.Div("__"*10),
            html.Div("Additionally, you can filter bike stations by entering an Address or a Landmark. You can also change the radius of your search."),
        ]),
    ],
    id="modal-lg",
    size="xl",
    is_open=True,
    centered=True
)

toast = dbc.Toast(
    id="graph-toast",
    is_open=False,
    dismissable=True,
    icon="dark",
    # top: 66 positions the toast below the navbar
    style={"position": "fixed", "top": 40, "right": 10, "width": 650},
    className="dash-bootstrap"
),


def home_layout():
    return [
        landing_modal,
        dcc.Graph(config={"displayModeBar": False}, style={"flex": "1 1 auto", "overflow": "hidden"}, id='map-graph'),
        html.Div(toast),
    ]


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/home":
        return home_layout()
    else:
        return home_layout()

@app.callback(
    Output('modal-lg', 'is_open'),
    [Input("close-lg", "n_clicks"),  Input("close-backdrop", "n_clicks")]
)
def close_modal(n):
    if n:
        return 'static'
    else:
        return 'static'

@app.callback(
    [Output('time-select-hour','options'), Output('time-select-hour','value')],
    [Input('time-select-day','date')]
)
def update_hour_dropdown(day):
    options = [{'label': t.strftime('%I:%M %p'), 'value': t.strftime('%Y-%m-%d %H')} for t in asts.timestamps if t.strftime('%Y-%m-%d') == day]
    return options, options[0]['value']

@app.callback(
    Output('party-size-num-label', 'children'),
    [Input("party-size", "value")]
)
def change_party_val(value):
    return 'Bikes Needed: ' + str(value)

@app.callback(
    Output('radius-num-label', 'children'),
    [Input("radius", "value")]
)
def change_party_val(value):
    return 'Search radius: ' + str(value) + ' m'

@app.callback(
    Output('map-graph', 'figure'),
    [Input('time-select-hour', 'value'),
     Input('party-size', 'value'),
     Input('place-filter','value'),
     Input('radius','value')],
    [State('map-graph', 'relayoutData')]
)
def update_graph(timeval, partyval, place_filter, r, relayout):
    timestamp = pd.to_datetime(timeval, format='%Y-%m-%d %H')

    partyval = int(partyval)
    mapbox = go.Figure()
    subset_predictions = asts.predictions.loc[asts.predictions['timestamps'] == timestamp, :]

    subset_predictions.loc[:,'colors'] = subset_predictions.loc[:, 'predicted_avail_bikes_cnt'].apply(
        lambda x: colorselector(x, partyval))

    merged = asts.bike_stations.merge(subset_predictions, left_on='dock_id', right_on='station_id', how='left')

    try:
        center_map = relayout['mapbox.center']
    except:
        center_map = dict(
                    lat=40.748,
                    lon=-73.986
                )

    if place_filter not in ['',None, []]:
        pos = {'lat': float(place_filter.split(',')[0]), 'long': float(place_filter.split(',')[1])}
        docks = filter_by_radius(merged, pos, int(r))
        merged = merged.loc[merged['dock_id'].isin(docks.values)]
        lats, lons = convert_circle_to_latlon(pos, int(r))
        mapbox.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            hoverinfo='none'
        ))
        center_map = dict(
                    lat=pos['lat'],
                    lon=pos['long']
                )

    trace_dict = {'rgb(255,0,0)': 'Unlikely bikes will be available',
                  'rgb(255,255,0)': 'Bikes may be available',
                  'rgb(0,255,0)': 'Likely bikes will be available',
                  'rgb(0,0,0)': 'No availability prediction'}

    merged.loc[:,'colors'] = merged.loc[:,'colors'].fillna('rgb(0,0,0)') # black for missing data
    print(merged['colors'].unique())
    for key in trace_dict.keys():
        mapbox.add_trace(go.Scattermapbox(
            lat=merged.loc[merged["colors"] == key, "_lat"],
            lon=merged.loc[merged["colors"] == key, "_long"],
            mode='markers',
            name=trace_dict[key],
            marker=go.scattermapbox.Marker(
                size=17,
                color= merged.loc[merged["colors"] == key, "colors"],
                opacity=0.7
            ),
            text=merged.loc[merged["colors"] == key, "dock_name"],
            hoverinfo='text'
        ))

    if relayout in ['', None, [], {'autosize': True}]:
        mapbox.update_layout(
            autosize=True,
            hovermode='closest',
            showlegend=True,
            legend=dict(x=0.01, y=0.99, 
                        bgcolor="rgba(40,40,40,0.7)", 
                        bordercolor="LightGray",
                        font={'color':"LightGray"}),
            mapbox=dict(
                accesstoken=public_token,
                bearing=0,
                center=center_map,
                pitch=0,
                zoom=12,
                style='dark'
            ),
            margin={"r": 0, "l": 0, "b": 0, "t": 0},
        )
    else:
        mapbox.update_layout(
            autosize=True,
            hovermode='closest',
            showlegend=True,
            legend=dict(x=0.01, y=0.99, 
                        bgcolor="rgba(40,40,40,0.7)", 
                        bordercolor="LightGray",
                        font={'color':"LightGray"}),
            mapbox=dict(
                accesstoken=public_token,
                bearing=relayout['mapbox.bearing'],
                center=center_map,
                pitch=relayout['mapbox.pitch'],
                zoom=relayout['mapbox.zoom'],
                style='dark'
            ),
            margin={"r": 0, "l": 0, "b": 0, "t": 0},
        )

    return mapbox


@app.callback(
    [Output('graph-toast', 'header'),
     Output('graph-toast', 'is_open'),
     Output('graph-toast', 'children')],
    [Input('map-graph', 'clickData'),
     Input('party-size','value')],
    [State('time-select-hour', 'value')]
)
def update_and_open_toast(clickdata, partyval, timeval):
    if clickdata:
        point_data = clickdata['points'][0]
        timestamp = pd.to_datetime(timeval, format='%Y-%m-%d %H')
        dock_id = asts.bike_stations.loc[point_data['pointIndex'], 'dock_id']
        start = max([timestamp-pd.Timedelta('6H'), asts.timestamps[0]]) # Pick the max between the selected time - 6 Hours or the minimum of available timestamps
        end = min([timestamp+pd.Timedelta('6H'), asts.timestamps[-1]]) # Same but opposite
        graph_data = asts.predictions.loc[(asts.predictions['station_id'] == dock_id) & 
                                            (asts.predictions['timestamps'] >= start) & 
                                            (asts.predictions['timestamps'] <= end), :].sort_values(by='timestamps')
        figure = {
            "data": [
                {
                    "x": graph_data.loc[:,'timestamps'],
                    "y": graph_data.loc[:,'predicted_avail_bikes_cnt'],
                    "type": "scatter",
                    "name": "Available Bikes Line"
                }]
            ,
            "layout": {"height": 420,
                       "barmode": 'relative',
                       "showlegend": False,
                       "margin": {"t": 40, "l": 60, "r": 40},
                       "plot_bgcolor": "rgba(0,0,0,0)",
                       "paper_bgcolor": "rgba(0,0,0,0.3)",
                       "font": {"color": "rgb(230,230,230)"},
                       "yaxis": {"title": "Predicted Bike Availability"},
                       'shapes': [
                                    # Line Horizontal
                                    {
                                        'type': 'line',
                                        'x0': start,
                                        'y0': partyval,
                                        'x1': end,
                                        'y1': partyval,
                                        'line': {
                                            'color': 'rgb(50, 171, 96)',
                                            'width': 4
                                        },
                                    }
                                ],}
        }
        return point_data['text'], True, dcc.Graph(figure=figure, config={'displayModeBar': False})
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    [Output("place-filter", "options"), 
     Output("place-filter", "value")],
    [Input("submit-button", "n_clicks")],
    [State("location-search","value"),
     State("place-filter","value")]
)
def on_button_click(n, loc, curr_val):
    if n and loc not in ['', None, []]:
        results = query_gp(loc)
        options = []
        for p in results.places:
            p.get_details()
            options += [{'label': p.formatted_address, 'value': str(p.geo_location['lat']) + "," + str(p.geo_location['lng'])}]
        print(options)
        if curr_val in options:
            return options, curr_val
        else:
            return options, None
    else:
        return [], None

port = int(os.environ.get('PORT', 8080))
server.run(debug=True, host="0.0.0.0", port=port)
