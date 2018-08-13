'''
 Autor: Joshua Prim, Philipp Krenitz, Bartos Mosch, Sophie Hagemann
 Version: 1.0

 Server für das hosten des FaSta-Dashboards

 Copyright 2018 The Authors. All Rights Reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
==============================================================================

'''
 
# -*- coding: utf-8 -*-
import dash
from dash.dependencies import State, Event, Output, Input
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dtb
import plotly
import dash_auth
import flask
import pandas
import csv
import datetime
import time
import os
import threading
import numpy as np

import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.offline import init_notebook_mode, plot, iplot as ppp


##########################################################################                 #############################################################################################################################################
########################################################################## Web Application #############################################################################################################################################
##########################################################################                 #############################################################################################################################################


class Dashboard():

    # Kostruktor
    def __init__(self):
       print('Fasta Server initialisiert!')
        

    def run(self):
         # Die Passworter eigentlich aus dem Quellcode-Repository heraushalten und in einer Datei oder einer Datenbank speichern.
        VALID_USERNAME_PASSWORD_PAIRS = [
            ['Josh', '1234'],
            ['Sophie', '1234']
        ]

        server = flask.Flask('EVA Dashboard')
        app = dash.Dash('EVA Dashboard', server=server)
        app.title = 'EVA Dashboard'
        auth = dash_auth.BasicAuth(
            app,
            VALID_USERNAME_PASSWORD_PAIRS
        )


        app.layout = html.Div(children=[

            # Überschrift
            html.Div([
                html.H1(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align':'center', 'width': '15em'},children='EVA Dashboard'),
            ]),

            # Berschreibung
            html.Div([
                html.H2(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align':'center', 'width': '10em'},children='Der Aufzugwächter'),
                dcc.Markdown('''
                    Informationen rund um Aufrüge und
                    Rolltreppen in Bahnhöfen der DB
                    Station & Service AG
                    '''.replace('  ', ''), className='beschreibung',
                containerProps={'style': {'maxWidth': '650px'}})
            ])
            
        ], style={'marginTop': '2%', 'marginLeft': '5%', 'marginRight': '5%'})


##########################################################################           #############################################################################################################################################
########################################################################## CALLBACKS #############################################################################################################################################
##########################################################################           #############################################################################################################################################


        #@app.callback():

        #app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
        
        app.run_server(debug=False, host='0.0.0.0')        


if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.run()
