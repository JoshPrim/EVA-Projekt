# -*- coding: utf-8 -*-
'''
 Autor: Joshua Prim, Philipp Krenitz, Bartos Mosch, Sophie Hagemann
 Version: 1.0

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

import sys
sys.path.append('./Clients')
from Postgres_Client import PostgreSQL_Zugriff
import psycopg2
import pgdb


##########################################################################                 #############################################################################################################################################
########################################################################## Web Application #############################################################################################################################################
##########################################################################                 #############################################################################################################################################


print('Fasta Server initialisiert!')

def getDesiredState(listWithStates: list, state: str):
    stateCounter = 0

    for i in listWithStates:

        if state == i['state']:
            stateCounter += 1

    return stateCounter


def getDesiredStateExplanation(listWithStates: list, state: str, stateExplanation: str):
    stateExpressionCounter = 0

    for i in listWithStates:

        if state == i['state'] and stateExplanation == i['stateExplanation']:
            stateExpressionCounter += 1

    return stateExpressionCounter

resultDictionary = {}
client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva', maxPoolSize=50)
dbeva = client.eva
facilities = dbeva['facilities']


############################################################
################# Die Aufzüge im Überblick #################
############################################################

resultOverview = facilities.aggregate([

    {'$match': {'type': 'ELEVATOR'}},
    {'$group': {
        '_id': '$equipmentnumber',
        'lastStateChangeDate': {'$last': '$datetime'},
        'state': {'$last': '$state'},
    }}
])

listWithStates = []

for i in resultOverview:
    listWithStates.append(i)

stateCountACTIVE = getDesiredState(listWithStates, 'ACTIVE')
stateCountINACTIVE = getDesiredState(listWithStates, 'INACTIVE')
stateCountUNKNOWN = getDesiredState(listWithStates, 'UNKNOWN')


####################################
###### Gründe für Inaktivität ######
####################################

uniqueList = facilities.distinct("stateExplanation");

resultGruendeFuerInaktivitaet = facilities.aggregate([

    {'$match': {'type': 'ELEVATOR'}},

    {'$group': {
        '_id': '$equipmentnumber',
        'lastStateChangeDate': {'$last': '$datetime'},
        'state': {'$last': '$state'},
        'stateExplanation': {'$last': '$stateExplanation'}

    }}
])

listWithStateExplanations = []

for i in resultGruendeFuerInaktivitaet:
    listWithStateExplanations.append(i)

dictStateExplanationReason = {}

for i in uniqueList:

    count = getDesiredStateExplanation(listWithStateExplanations, 'INACTIVE', str(i))

    if count != 0:
        dictStateExplanationReason[str(i)] = count
    
tmp1 = []
tmp2 = []

for key, value in dictStateExplanationReason.items():
    tmp1.append(key)
    tmp2.append(value)
    

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


        # Beschreibung
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



        # Übersicht
        html.Div([


            html.Div([ dcc.Graph(
            id='diagramm_status',
            figure={
                'data': [
                    {'x': ['aktiv', 'inaktiv', 'keine Information'], 'y': [stateCountACTIVE, stateCountINACTIVE, stateCountUNKNOWN], 'type': 'bar', 'name': 'Aufzüge',
                     'marker': dict(color=['green', 'red', 'orange'])
                     },
                ],
                'layout': {
                    'title': 'Die Aufzüge im Überblick',
                    'width': '35%',
                    'align': 'left'

                }
            }
            )], style={'width': '35%', 'text-align': 'left', 'display': 'inline-block', 'padding-top': 10, 'padding-left': 140, 'padding-bottom': 10 }),

            html.Div([ dcc.Graph(
            id='diagramm_inaktive',
            figure={
                'data': [
                    {'values': tmp2, 'type': 'pie', 'name': 'GründeInaktivität',
                     'marker': dict(colors=['#DCDCDC', '#778899', '#C0C0C0']), 'labels': tmp1
                     },
                ],
                'layout': {
                    'title': 'Gründe für Inaktivität',
                    'width': '35%',
                    'align': 'right'

                }
            }
            )],
            style={'width': '40%', 'text-align': 'right', 'display': 'inline-block', 'padding-left': 10, 'padding-bottom': 10}),

            html.Hr(),


        html.Div([
            html.H3(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'left',
                            'color': '#000099'}, children='Wusstest du schon?'),

            html.Div('Der älteste Aufzug steht in:[stadt] seit [Jahreszahl]'),
            html.Br(),
            html.Div('Der neuste Aufzug steht in:[stadt] seit [Jahreszahl]'),
            html.Br(),
            html.Div('Der Bahnhof mit den meisten Aufzügen steht in:[stadt]'),
            html.Br(),
            html.Div('Der Aufzug mit den meinste Ausfällen steht in:[stadt]'),

        ], style={'display': 'inline-block', 'text-align': 'left', 'margin-left': 50}),

        html.Hr(style={'width': 1, 'height': 200, 'display': 'inline-block', 'margin-left': 190}),


        html.Div([
            html.H3(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'left',
                               'color': '#000099'}, children='Aggregierte Werte'),

            html.Div('Berechnung 1'),
            html.Br(),
            html.Div('Berechnung 2'),
            html.Br(),
            html.Div('Berechnung 3'),
            html.Br(),
            html.Div('Berechnung 4'),

        ], style={'display': 'inline-block', 'text-align': 'left', 'margin-left': 100}),

        html.Hr(),


        html.H3(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'left',
                           'color': '#000099'}, children='Karte'),
            
        html.Div([
            html.Div('Stadt eingeben:  '),
            dcc.Input(id='karte_input', value='1', type='text'),
            html.Br()
        ]),
               
        html.Iframe(id='karte', srcDoc = open('map_inactive_elivators.html', 'r').read(), style={'width':'100%', 'height':'50em'}),
        


        ], style = {'background-color': '#E6E6FA'}
        )



], style={'marginTop': '2%', 'marginLeft': '5%', 'marginRight': '5%'})


##########################################################################           #############################################################################################################################################
########################################################################## CALLBACKS #############################################################################################################################################
##########################################################################           #############################################################################################################################################

@app.callback(
    Output(component_id='karte', component_property='srcDoc'),
    [Input(component_id='karte_input', component_property='value')]
)
def karte_aktualisieren(input_value):
    if input_value == '1':
        return open('map_inactive_elivators_FFM.html', 'r').read()
    else:
        return open('map_inactive_elivators.html', 'r').read()




app.run_server(debug=False, host='0.0.0.0', port='37002')



