# -*- coding: utf-8 -*-
'''
 Autor: Joshua Prim, Philipp Krenitz, Bartos Mosch, Sophie Hagemann
 Version: 1.3

 Server fuer das hosten des FaSta-Dashboards

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


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
import flask
import dash_auth
import json
import pymongo
import collections
from pprint import pprint
from bson.son import SON  # for aggregate function
from pymongo.command_cursor import CommandCursor
from types import *
import pandas as pd
import numpy as np
from pandas import DataFrame

import plotly.plotly as py
import plotly.graph_objs as go

import sys
sys.path.append('./Clients')
from Postgres_Client import PostgreSQL_Zugriff
import psycopg2
import pgdb
import folium
from geopy.geocoders import Nominatim


##########################################################################                 #############################################################################################################################################
########################################################################## Web Application #############################################################################################################################################
##########################################################################                 #############################################################################################################################################


print('Fasta Server initialisiert!')


resultDictionary = {}
client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva', maxPoolSize=50)
dbeva = client.eva
facilities = dbeva['facilities']



# Zoom am ausgewählten Ort
geolocator = Nominatim(user_agent="Eva_Dashboard")
####################################
######        APP             ######
####################################

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
        html.H1(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center', 'width': '15em'},
                children='EVA Dashboard'),
    ]),

    # Unterüberschrift
    html.Div([
        html.Hr(),

        html.H1(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center', 'width': '10em',
                       'color': '#000099'}, children='Der Aufzugwächter'),
        dcc.Markdown('''
        **Informationen rund um Aufzüge und Rolltreppen in Bahnhöfen der DB Station & Service AG**
        '''.replace('  ', ''), className='beschreibung',
                     containerProps={
                         'style': {'maxWidth': '650px', 'color': '#000099', 'margin-left': 'auto',
                                   'margin-right': 'auto', 'text-align': 'center'}})
    ]),

    html.Div([
        dcc.Link('Go to Page Aufzüge', href='')
    ], style={'text-align': 'left'}),

    # Hauptteil
    html.Div([

        # Diagramme
        html.Div([], style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            html.Div([dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Bar(
                            x = [3,6,4],
                            y = ['NaN', 'inaktiv', 'aktiv'],
                            orientation = 'h',
                            marker= dict(color=['red', 'orange', 'green'])
                        )
                    ]
                ), id='diagramm_uebersicht'
            )], style={'width': '40%', 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10}),

            html.Div([dcc.Graph(

                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x = np.linspace(0, 1, 30),
                            y = np.random.randn(30),
                            mode = 'lines+markers',
                            name = 'Zeitreihe'
                        )
                    ]
                ), id='diagramm_zeitverlauf'
            )], style={'width': '40%', 'display': 'inline-block', 'padding-left': 10, 'padding-bottom': 10}),
        ], style={'width': '90%', 'margin': 'auto', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Hr(),




        #Karte
        html.Div([
            #Titel
            html.Div([
                html.H3(style={'margin-right': 'auto', 'text-align': 'left',
                           'color': '#000099'}, children='Funktionieren die Rolltreppen an deiner Haltestelle? - Finde es heraus!'),
            ]),
            #linker Teil
            html.Div([

                html.Div(['Stadt:  '],
                         style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='stadt_input', value='Frankfurt', type='text',
                          style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Div(['Bundesland:  '],
                         style={'margin-left': '15', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='bundesland_input', value='Hessen', type='text',
                          style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Br(), html.Br(),
                dcc.RadioItems(
                    id='radio_button',
                    options=[
                        {'label': 'Aktive Rolltreppen', 'value': 'aktiv'},
                        {'label': 'Inaktive Rolltreppen', 'value': 'inaktiv'},
                        {'label': ' Alle Rolltreppen', 'value': 'beide'}
                    ],
                    value='inaktiv', style={'margin-left': 10}
                ),
                html.Iframe(id='karte', srcDoc=open('map_inactive_elivators.html', 'r').read(),
                            style={'width': '90%', 'height': '30em'})

            ], style={'width': '49%', 'display': 'inline-block'}),

            # rechter Teil
            html.Div([
                html.Br(), html.Br(),
                html.Div(['Rolltreppen-ID:  '],
                         style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='rolltreppen_id_input', type='text',
                          style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Br(),
                html.Hr(),

                # Tabelle
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        columns=['Datum_Uhrzeit', 'Status', 'Erklärung des Status'],
                        editable=False,
                        row_selectable=False,
                        filterable=False,
                        sortable=False,
                        id='datatable-status-rolltreppen',
                        selected_row_indices=[],
                        min_height=400
                    ),

                    html.Br(),
                ])




             ], style={'width': '49%','display': 'inline-block', 'vertical-align':'top'}),

        ], style={'margin-left': '20'}),
    ], style={'background-color': '#E6E6FA'}),


    #Fußzeile
    html.Div([ ], style={'height':70}),
    html.Hr(),
    html.Div([

        dcc.Markdown(''' 
                **THM Friedberg**
                '''.replace('  ', ''), className='beschreibung',
                     containerProps={
                         'style': {'maxWidth': '650px', 'color': '#000000', 'margin-left': 'auto',
                                   'margin-right': 'auto', 'text-align': 'center'}}),

        dcc.Markdown(''' 
                **Sophie Hagemann, Philipp Krenitz, Bartos Mosch, Joshua Prim**
                '''.replace('  ', ''), className='beschreibung',
                         containerProps={
                             'style':{'maxWidth': '650px', 'color': '#000000', 'margin-left': 'auto',
                                       'margin-right': 'auto', 'text-align': 'center'}})
    ], style={'height':70}),


], style={'marginTop': '2%', 'marginLeft': '5%', 'marginRight': '5%'})




##########################################################################           #############################################################################################################################################
########################################################################## CALLBACKS #############################################################################################################################################
##########################################################################           #############################################################################################################################################

# Callback Tabelle aktualisieren

'''
@app.callback(
    Output(component_id='datatable-status-rolltreppen', component_property='rows'),
    [Input(component_id='rolltreppen_id_input', component_property='value')]
)
def tabelle_aktualisieren(input_value):
    try:


    except:
        return [{}]

'''






app.run_server(debug=False, host='0.0.0.0', port='37002')