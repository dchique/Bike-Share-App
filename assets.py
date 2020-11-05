import plotly.graph_objs as go
import base64
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import glob
import os
import pandas as pd
import numpy as np
from datetime import datetime as dt



class Assets:
    def __init__(self):
        self.selected_link_style = {
            "display": "block",
            "color": "white",
            "backgroundColor": "grey",
            "fontSize": 16,
            "padding": "5px 30px",
            "text-decoration": "none",
            "borderRight": "5px solid #da1f33",
        }
        self.unselected_link_style = {
            "display": "block",
            "color": "white",
            "backgroundColor": "grey",
            "fontSize": 16,
            "padding": "5px 30px",
            "text-decoration": "none",
        }

        brand_im = "./assets/bikecast.png"
        
        self.brand_im = base64.b64encode(open(brand_im, "rb").read())  # Brand Logo

        self.predictions = pd.read_csv("./Tools/all_predictions.csv")
        self.predictions.loc[:, 'timestamps'] = pd.to_datetime((self.predictions.loc[:,'date'] + ' ' + self.predictions['hour'].astype(str) + ':00'))
        self.stations = self.predictions.loc[:,'station_id'].unique()
        self.timestamps = pd.to_datetime(self.predictions.loc[:,'timestamps'].sort_values().unique())

        self.bike_stations = pd.read_csv("./Tools/bikeshare_nyc_stations.csv")
        self.bike_stations = self.bike_stations.loc[self.bike_stations['dock_id'].isin(self.stations)].reset_index()
        print(len(self.bike_stations))
        #self.current_time = self.current_time = pd.to_datetime('08/24/2020 23:59').floor('1H')
        # for i in range(0,24,1):
        #     self.timestamps += [(self.current_time + pd.Timedelta('1H')*i)]

        # self.bike_stations.loc[:,'available_bikes'] = pd.Series([{t.strftime('%Y-%m-%d %H') : np.random.randint(low = 0, high = 20) for t in self.timestamps} for dex in self.bike_stations.index])

        # self.hours = []
        # for i in range(0,24):
        #     hour = '%d:00' % i
        #     self.hours.append({'label': hour, 'value': hour})

        datePicker = dbc.Col(
            dcc.DatePickerSingle(
                id='time-select-day',
                min_date_allowed= self.timestamps[0].date(),
                max_date_allowed= self.timestamps[-1].date(),
                initial_visible_month= self.timestamps[0].date(),
                date= self.timestamps[0].date()
            ),
            width=6
        )
        timePicker = dbc.Col(
            dcc.Dropdown(id='time-select-hour'),
            width=6
        )
        self.controls = html.Div([
            html.Label('Set a pick-up date and time:', className='mt-3'),
            dbc.Row([datePicker, timePicker]),
            html.Label('Set number of bikes needed:', className='mt-3'),
            dbc.Input(bs_size="sm", id="party-size", type="range", max=50, min=1, step=1, value=1),
            html.Label(id='party-size-num-label', className='mt-1'),
            html.Div('Search for stations nearby:', className='mt-3'),
            dbc.Input(type='text', placeholder='Enter address or landmark...', id='location-search'),
            html.Div(dbc.Button('Search places', id='submit-button', color='dark', block=True, className='mt-3')),
            dbc.RadioItems(id='place-filter', className='mt-3')
        ], className='dash-bootstrap')

    def navbar(self):

        navbar = dbc.Navbar(
            [
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        # dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Col(
                            html.Img(
                                src="data:image/png;base64,{}".format(
                                    self.brand_im.decode()
                                ),
                                height="40px",
                            ),
                            className="ml-3"
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("BikeCast", className="ml-5")
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                ),

            ],
            expand=False,
            dark=True,
            color="secondary"
        )
        return navbar

    def sidebar(self):
        nav = dbc.Nav(
                [
                    html.Div(id="nav-bar", children=dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="data:image/png;base64,{}".format(self.brand_im.decode()),
                                    height="40px",
                                )
                            ),
                            dbc.Col(dbc.NavbarBrand("BikeCast")),
                        ],
                        className="nav-bar",
                        align="center",
                        no_gutters=True,
                    )),
                    dbc.Row(
                        [dbc.Col(dbc.Nav(self.controls, navbar=True))],
                        no_gutters=True,
                        className="side-bar-pad",
                        align="center"
                    )
                ],
                vertical="lg",
            )
        return nav


if __name__ == "__main__":
    asts = Assets()