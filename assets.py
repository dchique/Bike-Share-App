import plotly.graph_objs as go
import base64
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import glob
import os
import pandas as pd
import numpy as np
import datetime


class Assets:
    def __init__(self):
        self.selected_link_style = {
            "display": "block",
            "color": "white",
            "backgroundColor": "#193f5f",
            "fontSize": 16,
            "padding": "5px 30px",
            "text-decoration": "none",
            "borderRight": "5px solid #da1f33",
        }
        self.unselected_link_style = {
            "display": "block",
            "color": "white",
            "backgroundColor": "#002a4e",
            "fontSize": 16,
            "padding": "5px 30px",
            "text-decoration": "none",
        }

        brand_im = "./assets/bikecast.png"
        
        self.brand_im = base64.b64encode(open(brand_im, "rb").read())  # Brand Logo

        self.bike_stations = pd.read_csv("./Tools/bikeshare_nyc_stations.csv")
        self.current_time = pd.to_datetime('today').floor('3H')
        self.timestamps = []
        for i in range(0,8,1):
            self.timestamps += [(self.current_time + pd.Timedelta('3H')*i)]

        self.bike_stations.loc[:,'available_bikes'] = pd.Series([[np.random.randint(low = 0, high = 20) for t in self.timestamps] for dex in self.bike_stations.index])

        self.dropdown_options = [
                        dbc.DropdownMenuItem(header=True, id='party-size-num-label'),
                        dbc.DropdownMenuItem(dbc.Input(bs_size="sm", id="party-size", type="range", max=10, min=1, step=1, value=1),header=True),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem(header=True, id='arrival-time-label'),
                        dbc.DropdownMenuItem(dbc.Input(type="range", bs_size="sm", id="time-select", min=0, max=len(self.timestamps)-1, step=1, value=1), header=True),
                    ]

        self.dropdown = [
            dbc.DropdownMenu(
                    children=self.dropdown_options,
                    nav=True,
                    in_navbar=True,
                    label="Settings",
                    right=True,
                    style= {'width':'200px'}
                )
        ]

    def navbar(self):

        navbar = dbc.Navbar(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src="data:image/png;base64,{}".format(
                                        self.brand_im.decode()
                                    ),
                                    height="40px",
                                )
                            ),
                            dbc.Col(
                                dbc.NavbarBrand("BikeCast", className="ml-3")
                            ),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    href="",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    [
                    dbc.Row(
                        [dbc.Col(dbc.Nav(self.dropdown, navbar=True))],
                        no_gutters=True,
                        className="ml-auto flex-nowrap mt-3 mt-md-0",
                        align="center"
                    )
                    ],
                    id="navbar-collapse",
                    navbar=True,
                ),
            ],
            dark=True,
            color="dark"
        )
        return navbar


if __name__ == "__main__":
    asts = Assets()