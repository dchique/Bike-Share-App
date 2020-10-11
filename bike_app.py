import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from assets import Assets
import os

asts = Assets()

app = dash.Dash(
    name="BikeCast",
    #url_base_pathname=r"/home/",
    external_stylesheets= [dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="BikeCast - NYC - test"
)

server = app.server

