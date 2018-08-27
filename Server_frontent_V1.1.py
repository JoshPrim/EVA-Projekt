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

def getDesiredState(listWithStates, state):
    stateCounter = 0

    for i in listWithStates:

        if state == i['state']:
            stateCounter += 1

    return stateCounter


def getDesiredStateExplanation(listWithStates, state, stateExplanation):
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
    
key_array = []
value_array = []

for key, value in dictStateExplanationReason.items():
    key_array.append(key)
    value_array.append(value)



aufzüge = pd.read_csv('Stammdaten_Aufzüge.csv', sep= ';', engine='python')

columns = ['Standort Equipment', 'TechnPlatzBezeichng', 'Equipment', 'Equipmentname','Ort','Wirtschaftseinheit','Hersteller',
          'Baujahr','ANTRIEBSART','ANZAHL_HALTESTELLEN','ANZAHL_TUEREN_KABINE', 'ANZAHL_TUEREN_SCHACHT', 'FOERDERGESCHWINDIGKEIT',
           'FOERDERHOEHE', 'LAGE', 'TRAGKRAFT', 'ERWEITERTE_ORTSANGABE', 'MIN_TUERBREITE', 'KABINENTIEFE', 'KABINENBREITE',
           'KABINENHOEHE', 'TUERHOHE', 'FABRIKNUMMER', 'TUERART','GEOKOORDINATERECHTSWERT','GEOKOORDINATEHOCHWERT', 'AUSFTEXTLICHEBESCHREIBUNG']
aufzüge.columns = columns
aufzüge = aufzüge.drop(0)
aufzüge['Equipment'] = aufzüge['Equipment'].astype(str).astype('int64')



####################################
######         Karte          ######
####################################

elevators = facilities.aggregate([

    {'$match': {'type': 'ELEVATOR'}},
    {'$group': {
        '_id': '$equipmentnumber',
        'description': {'$last': '$description'},
        'geocoordX': {'$last': '$geocoordX'},
        'geocoordY': {'$last': '$geocoordY'},
        'lastStateChangeDate': {'$last': '$datetime'},
        'state': {'$last': '$state'},
    }}
])

elevators = pd.DataFrame(list(elevators))
elevators.columns = ['equipmentnumber', 'description', 'geocoordX', 'geocoordY', 'lastStateChangeDate', 'state']

inactive = elevators[elevators['state'] == 'INACTIVE']

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

        # Hauptteil
        html.Div([
            #Diagramme
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
                    {'values': value_array, 'type': 'pie', 'name': 'GründeInaktivität',
                     'marker': dict(colors=['#DCDCDC', '#778899', '#C0C0C0']), 'labels': key_array
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

        #mittleres Drittel: "Wusstest du schon?", aggregierte Werte etc.
        html.Div([]),
        html.Div([
            html.H3(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'right',
                            'color': '#000099'}, children='Wusstest du schon?'),

            html.Div('Der älteste Aufzug steht in: '),
            html.Div(id='aeltester_aufzug', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
            html.Div('Der neuste Aufzug steht in: '),
            html.Div(id='neuster_aufzug', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
            html.Div('Die Station mit den meisten Aufzügen steht in: '),
            html.Div(id='meisten_aufzüge', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
            html.Div('Der Aufzug mit den meinste Ausfällen steht in: '),
            html.Div(id='meiste_ausfälle', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
        ], id='wusstest_du_schon', style={'display': 'inline-block', 'text-align': 'right', 'width': '45%', 'margin-right':20}),

        html.Hr(style={'width': 1, 'height': 150, 'display': 'inline-block'}),

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
            html.Br(),
        ], style={'display': 'inline-block', 'text-align': 'left', 'width': '50%', 'margin-left':20}),

        html.Hr(),

        #unteres Drittel
        html.Div([
            #Titel
            html.Div([
                html.H3(style={'margin-right': 'auto', 'text-align': 'left',
                           'color': '#000099'}, children='Funktionieren die Aufzüge an deiner Haltestelle? - Finde es heraus!'),
            ]),
            html.Div([]),
            #linker Teil
            html.Div([
                html.Div(['Stadt:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='stadt_input', value='Frankfurt', type='text', style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Div(['Bundesland:  '], style={'margin-left': '15', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='bundesland_input', value='Hessen', type='text', style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Br(), html.Br(),
                dcc.RadioItems(
                    options=[
                        {'label': 'Aktive Aufzüge', 'value': 'aktiv'},
                        {'label': 'Inaktive Aufzüge', 'value': 'inaktiv'},
                        {'label': ' Alle Aufzüge', 'value': 'beide'}
                    ],
                    value='inaktiv', style={'margin-left':10}
                ),
                html.Iframe(id='karte', srcDoc=open('map_inactive_elivators.html', 'r').read(),
                            style={'width': '90%', 'height': '30em'})
            ], style={'width': '49%', 'display': 'inline-block'}),

            #rechter Teil
            html.Div([
                html.Br(), html.Br(),
                html.Div(['Aufzug-ID:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='aufzug_id_input', type='text',
                          style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Br(),
                html.Hr(),
                    html.Div([
                        html.Div(['Stationsname:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(['Beschreibung:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(['Hersteller:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(['Antriebsart:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(['Baujahr:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                    ], style={'width': '20%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div(id='stationsname', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(id='beschreibung', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(id='hersteller',style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(id='antrieb', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                        html.Div(id='baujahr', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                        html.Br(), html.Br(),
                    ], style={'width': '80%', 'display': 'inline-block'}),

                # Tabelle
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        columns=['Datum', 'Status' , 'Erklärung des Status'],
                        editable=False,
                        row_selectable=False,
                        filterable=False,
                        sortable=False,
                        id='datatable-status',
                        selected_row_indices=[],
                        min_height=250
                    ),

                    html.Br(),
                ])

            ], style={'width': '49%','display': 'inline-block', 'vertical-align':'top'})
         ], style={'margin-left':'20'}),

        ], style = {'background-color': '#E6E6FA'}),


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

# Callback Karte aktualisieren
@app.callback(
    Output(component_id='karte', component_property='srcDoc'),
    [Input(component_id='stadt_input', component_property='value'),
     Input(component_id='bundesland_input', component_property='value')]
)
def karte_aktualisieren(input_stadt, input_bland):
    try: 
        input_user = str(input_stadt + ', ' + input_bland + ', Deutschland')
        location = geolocator.geocode(input_user)

        m = folium.Map(location=[location.latitude,location.longitude], zoom_start=10)

        for i, row in inactive.iterrows():
            if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                pass
            else:
                tmp = str('ID: '+ str(row['equipmentnumber'])+ ' Beschreibung: '+ str(row['description']))
                folium.Marker([row['geocoordY'], row['geocoordX']], 
                              popup = tmp,
                             icon=folium.Icon(color='red', icon='info-sign')).add_to(m)

        m.save('map_inactive_elivators.html')
        return open('map_inactive_elivators.html', 'r').read()
    
    except:    
        return open('map_inactive_elivators_FFM.html', 'r').read()

# Callback Stationsname aktualisieren
@app.callback(
    Output(component_id='stationsname', component_property='children'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def stationsname_aktualisieren(input_value):
    try:
        aufzug = aufzüge[aufzüge['Equipment'] == int(input_value)]
        attribute = aufzug['Ort'].values
        return attribute[0]

    except:
        return str('Aufzug existiert nicht!')


# Callback Hersteller aktualisieren
@app.callback(
    Output(component_id='hersteller', component_property='children'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def hersteller_aktualisieren(input_value):
    try:
        aufzug = aufzüge[aufzüge['Equipment'] == int(input_value)]
        attribute = aufzug['Standort Equipment'].values
        return attribute[0]

    except:
        return ''


# Callback Beschreibung aktualisieren
@app.callback(
    Output(component_id='beschreibung', component_property='children'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def beschreibung_aktualisieren(input_value):
    try:
        tmp3 = aufzüge[aufzüge['Equipment'] == int(input_value)]
        attribute = tmp3['Hersteller'].values
        return attribute[0]

    except:
        return ''


# Callback Antriebsart aktualisieren
@app.callback(
    Output(component_id='antrieb', component_property='children'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def anstriebsart_aktualisieren(input_value):
    try:
        aufzug = aufzüge[aufzüge['Equipment'] == int(input_value)]
        attribute = aufzug['ANTRIEBSART'].values
        return attribute[0]

    except:
        return ''


# Callback Baujahr aktualisieren
@app.callback(
    Output(component_id='baujahr', component_property='children'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def baujahr_aktualisieren(input_value):
    try:
        aufzug = aufzüge[aufzüge['Equipment'] == int(input_value)]
        attribute = aufzug['Baujahr'].values
        return attribute[0]

    except:
        return ''


# Callback Tabelle aktualisieren
@app.callback(
    Output(component_id='datatable-status', component_property='rows'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def tabelle_aktualisieren(input_value):
    try:
        tabellen_input = facilities.find({"type": "ELEVATOR", "equipmentnumber": int(input_value)})
        tabellen_input = pd.DataFrame(list(tabellen_input))
        tabellen_input = tabellen_input[['datetime', 'state', 'stateExplanation']]
        status_tabelle = tabellen_input[::-1]
        status_tabelle.columns = ['Datum', 'Status' , 'Erklärung des Status']

        return status_tabelle.to_dict('records')

    except:
        return [{}]

'''
#Callback "Wusstest du schon?" aktualisieren
@appcallback(
    Output(component_id='aeltester_aufzug', component_property='children'),
    [Input(component_id='', component_property='' )]
)
def aeltester_aufzug_berechnen
    value = '[stadt] seit [Jahreszahl]'

@appcallback(
    Output(component_id='neuster_aufzug', component_property='children'),
    [Input(component_id='', component_property='')]
)
def aneuster_aufzug_berechnen
    value = '[stadt] seit [Jahreszahl]'


@appcallback(
    Output(component_id='meisten_aufzüge', component_property='children'),
    [Input(component_id='', component_property='')]
)
def meisten_aufzüge_berechnen
    value = '[stadt] [Anzahl]'

@appcallback(
    Output(component_id='meiste_ausfälle', component_property='children'),
    [Input(component_id='', component_property='')]
)
def meiste_ausfälle_berechnen
    value = '[stadt]'

'''


app.run_server(debug=False, host='0.0.0.0', port='37002')

