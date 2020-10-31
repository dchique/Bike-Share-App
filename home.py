import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State, ALL, MATCH
# import Pages.marine, Pages.offshore, Pages.lookup, Pages.drilldown, Pages.configure, Pages.start, Pages.removal
from bike_app import app, server, asts
import os

public_token = 'pk.eyJ1IjoiZGNoaXF1ZTMiLCJhIjoiY2tmdmg5Y2FjMTFmbzJzczMwcnRhMG50bCJ9.JgdIR-3Nkxb2hRc-5UQ79w'


def colorselector(num_of_bikes, val):
    if num_of_bikes < val:
        #color = 'rgb(255,0,0)'
        color = 'rgb(0,255,0)'
    elif num_of_bikes - 2 < val:
        #color = 'rgb(255,255,0)'
        color = 'rgb(0,255,0)'
    elif num_of_bikes > val:
        color = 'rgb(0,255,0)'
    return color


# page = "/home" hello
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="nav-bar-div", children=asts.navbar()),
        html.Div(id="page-content", style={"display": "flex",
                                           "flex-flow": "column",
                                           "height": "100%",
                                           "flex": "1 1 auto"}),
        # sidebar
    ], style={"display": "flex",
              "flex-flow": "column",
              "height": "100%"}
)

landing_modal = dbc.Modal(
    [
        dbc.ModalHeader("Welcome to BikeCast for NYC!", style={'justify-content': 'center'}),
        dbc.ModalBody(
            "You can use BikeCast to browse through citibike statikons in NYC. Set a time and party size to see predicted availability at a future time!"),
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
    icon="info",
    # top: 66 positions the toast below the navbar
    style={"position": "fixed", "top": 82, "left": 10, "width": 450},
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
    Output('party-size-num-label', 'children'),
    [Input("party-size", "value")]
)
def change_party_val(value):
    return 'Party Size: ' + str(value)


@app.callback(
    Output('arrival-time-label', 'children'),
    [Input("time-select", "value")]
)
def change_time_val(value):
    value = int(value)
    return 'Arrival Time: ' + asts.timestamps[value].strftime('%b %d, %H:%M')


@app.callback(
    Output('map-graph', 'figure'),
    [Input('time-select', 'value'),
     Input('party-size', 'value')],
    [State('map-graph', 'relayoutData')]
)
def update_graph(timeval, partyval, relayout):
    timeval = int(timeval)
    partyval = int(partyval)
    mapbox = go.Figure()

    bike_station_colors = asts.bike_stations.loc[:, 'available_bikes'].apply(
        lambda x: colorselector(x[timeval], partyval))

    mapbox.add_trace(go.Scattermapbox(
        lat=asts.bike_stations["_lat"],
        lon=asts.bike_stations["_long"],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=17,
            color=bike_station_colors,
            opacity=0.7
        ),
        text=asts.bike_stations["dock_name"],
        hoverinfo='text'
    ))

    if relayout in ['', None, []]:
        mapbox.update_layout(
            autosize=True,
            hovermode='closest',
            showlegend=False,
            mapbox=dict(
                accesstoken=public_token,
                bearing=0,
                center=dict(
                    lat=40.748,
                    lon=-73.986
                ),
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
            showlegend=False,
            mapbox=dict(
                accesstoken=public_token,
                bearing=relayout['mapbox.bearing'],
                center=relayout['mapbox.center'],
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
    [Input('map-graph', 'clickData')]
)
def update_and_open_toast(clickdata):
    if clickdata:
        point_data = clickdata['points'][0]
        figure = {
            "data": [
                {
                    "x": asts.timestamps,
                    "y": asts.bike_stations.loc[point_data['pointIndex'], 'available_bikes'],
                    "type": "scatter",
                    "name": "Available Bikes Line"
                }]
            ,
            "layout": {"height": 320,
                       "barmode": 'relative',
                       "showlegend": False,
                       "margin": {"t": 40, "l": 40, "r": 40},
                       "plot_bgcolor": "rgba(0,0,0,0)",
                       "paper_bgcolor": "rgba(0,0,0,0.3)",
                       "font": {"color": "rgb(230,230,230)"}}
        }
        return point_data['text'], True, dcc.Graph(figure=figure, config={'displayModeBar': False})
    return dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


port = int(os.environ.get('PORT', 8080))
server.run(debug=True, host="0.0.0.0", port=port)
