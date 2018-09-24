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
import sys
import dash
import dash_auth
import dash_core_components
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import flask
import pandas as pd
import plotly.graph_objs as go
import pymongo
import threading
from dash.dependencies import Input, Output
import os
import collections
from pprint import pprint
from pymongo.command_cursor import CommandCursor
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from types import *
import pandas as pd
import numpy as np
from pandas import DataFrame

sys.path.append('./Clients')
import folium
from geopy.geocoders import Nominatim
#from sqlalchemy import create_engine
import psycopg2

##########################################################################                 #############################################################################################################################################
########################################################################## Web Application #############################################################################################################################################
##########################################################################                 #############################################################################################################################################

# Konstanten
MONGO_URL = os.environ.get('MONGO_URI')
POSTGRESS_URL = os.environ.get('POSTGRES_URL')
HOST_ID = '0.0.0.0'
PORT = '37002'

print('Fasta Server initialisiert!')

def createGraphDataForEscalatorPage(numberOfLastEntries: int):

    ergDF = pd.DataFrame(columns=['Datum', 'Anzahl_Ausfälle'])

    facilities_collection = facilities.find({})

    pandas_facilities = pd.DataFrame(list(facilities_collection))

    pandas_facilities = pandas_facilities[['equipmentnumber', 'datetime', 'state']]
    facilities_distinct = pandas_facilities
    facilities_distinct.columns = ['ID', 'Datum', 'Status']

    facilities_distinct['Datum'] = pd.to_datetime(facilities_distinct['Datum'], format="%Y-%m-%d_%H-%M-%S")
    facilities_distinct['Datum'] = facilities_distinct['Datum'].dt.strftime('%Y-%m-%d')

    facilities_distinct_inactive = facilities_distinct[facilities_distinct['Status'] == 'INACTIVE']

    dfOnlyDatetime = pd.DataFrame(facilities_distinct_inactive['Datum'], columns=['Datum']).drop_duplicates()

    facilities_distinct_inactive_latestDate = facilities_distinct_inactive.groupby('ID')['Datum'].max()

    counter = 0
    for index, row in dfOnlyDatetime.iterrows():

        counter = 0

        for key, value in facilities_distinct_inactive_latestDate.items():

            if value == row['Datum']:
                counter += 1

        ergDF.loc[index] = row['Datum'], counter

    ergDF = ergDF.reset_index().drop(['index'], axis=1)

    ergDF = ergDF.iloc[-numberOfLastEntries:]

    return ergDF


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


def createOverview(givenType: str):

    resultOverview = facilities.aggregate([

        {'$match': {'type': givenType}},
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

    return stateCountACTIVE, stateCountINACTIVE, stateCountUNKNOWN


def createReasonsForInactivity(givenType: str):

    uniqueList = facilities.distinct("stateExplanation");

    resultGruendeFuerInaktivitaet = facilities.aggregate([

        {'$match': {'type': givenType}},

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

    return key_array, value_array


def createInitialData():

    client = pymongo.MongoClient(MONGO_URL, maxPoolSize=50)
    dbeva = client.eva_dev
    facilities = dbeva['facilities']

    # Aufzüge reinladen
    conn = psycopg2.connect(host='station-db', user='postgres', password='postgres', dbname='eva_dev', port=5432)
    cur = conn.cursor()

    querry = 'select * from "elevator"'
    cur.execute( querry )

    stammdaten_liste = cur.fetchall()

    aufzüge = pd.DataFrame(stammdaten_liste)

    columns = ['ID','Standort Equipment', 'TechnPlatzBezeichng', 'Equipment', 'Equipmentname', 'Ort', 'Wirtschaftseinheit',
               'Hersteller',
               'Baujahr', 'ANTRIEBSART', 'ANZAHL_HALTESTELLEN', 'ANZAHL_TUEREN_KABINE', 'ANZAHL_TUEREN_SCHACHT',
               'FOERDERGESCHWINDIGKEIT',
               'FOERDERHOEHE', 'LAGE', 'TRAGKRAFT', 'ERWEITERTE_ORTSANGABE', 'MIN_TUERBREITE', 'KABINENTIEFE',
               'KABINENBREITE',
               'KABINENHOEHE', 'TUERHOHE', 'FABRIKNUMMER', 'TUERART', 'GEOKOORDINATERECHTSWERT',
               'GEOKOORDINATEHOCHWERT', 'AUSFTEXTLICHEBESCHREIBUNG']
    aufzüge.columns = columns
    aufzüge = aufzüge.drop(0)
    aufzüge['Equipment'] = aufzüge['Equipment'].astype(str).astype('int64')
    aufzüge = aufzüge.drop_duplicates(['Equipment'])
    aufzüge = aufzüge.drop(columns=['ID'])
    aufzüge = aufzüge.fillna(value=np.nan)
    aufzüge['Baujahr'] = pd.to_numeric(aufzüge['Baujahr'], errors='coerce')

    print('Anzahl Aufzüge: ', len(aufzüge))

    return facilities, aufzüge


def createMap(givenType: str):

    resultCommandCursor = facilities.aggregate([

        {'$match': {'type': givenType}},
        {'$group': {
            '_id': '$equipmentnumber',
            'description': {'$last': '$description'},
            'geocoordX': {'$last': '$geocoordX'},
            'geocoordY': {'$last': '$geocoordY'},
            'lastStateChangeDate': {'$last': '$datetime'},
            'state': {'$last': '$state'},
        }}
    ])

    resultCommandCursor = pd.DataFrame(list(resultCommandCursor))
    resultCommandCursor.columns = ['equipmentnumber', 'description', 'geocoordX', 'geocoordY', 'lastStateChangeDate', 'state']

    inactive = resultCommandCursor[resultCommandCursor['state'] == 'INACTIVE']
    active = resultCommandCursor[resultCommandCursor['state'] == 'ACTIVE']

    # Zoom am ausgewählten Ort
    geolocator = Nominatim(user_agent="Eva_Dashboard")

    return inactive, active, geolocator


#####################################################################
################ Start of Code (create initial data) ################
#####################################################################

facilities, aufzüge = createInitialData()


############################################################
################# Die Aufzüge im Überblick #################
############################################################

elevatorStateCountACTIVE, elevatorStateCountINACTIVE, elevatorStateCountUNKNOWN = createOverview('ELEVATOR')


############################################################
############### Die Rolltreppen im Überblick ###############
############################################################

escalatorStateCountACTIVE, escalatorStateCountINACTIVE, escalatorStateCountUNKNOWN = createOverview('ESCALATOR')


####################################################
###### Gründe für Inaktivität von Fahrstühlen ######
####################################################

elevator_key_array, elevator_value_array = createReasonsForInactivity('ELEVATOR')


####################################################
###### Gründe für Inaktivität von Rolltreppen ######
####################################################

escalator_key_array, escalator_value_array = createReasonsForInactivity('ESCALATOR')


####################################################
######   Routine zum Aktualisieren der Daten  ######
####################################################

def updateValues():
    global facilities, aufzüge, elevatorStateCountACTIVE, elevatorStateCountINACTIVE, elevatorStateCountUNKNOWN
    global escalatorStateCountACTIVE, escalatorStateCountINACTIVE, escalatorStateCountUNKNOWN
    global elevator_key_array, elevator_value_array
    global escalator_key_array, escalator_value_array

    facilities, aufzüge = createInitialData()
    elevatorStateCountACTIVE, elevatorStateCountINACTIVE, elevatorStateCountUNKNOWN = createOverview('ELEVATOR')
    escalatorStateCountACTIVE, escalatorStateCountINACTIVE, escalatorStateCountUNKNOWN = createOverview('ESCALATOR')
    elevator_key_array, elevator_value_array = createReasonsForInactivity('ELEVATOR')
    escalator_key_array, escalator_value_array = createReasonsForInactivity('ESCALATOR')

# Daten werden jede Stunde aktualisiert
scheduler = BlockingScheduler()
scheduler.add_job(updateValues, 'interval', hours=1)

class UpdateValue(threading.Thread):
    def __init__(self):
            threading.Thread.__init__(self)
    def run(self):
        scheduler.start()
        print('Thread zum Updaten der Werte gestartet!')

tread = UpdateValue()
tread.start()

####################################
######   Wusstest du schon?   ######
####################################

# Ältester Aufzug
aeltesteAufzug_datensatz = aufzüge[aufzüge['Baujahr'] == int(aufzüge['Baujahr'].min())]

aeltesteAufzug_ort = aeltesteAufzug_datensatz['Ort'].values[0]
aeltesteAufzug_jahr = int(aeltesteAufzug_datensatz['Baujahr'].values[0])

# Station mit den meisten Aufzügen
uniquelist_orte = aufzüge['Ort'].unique()

df_anzahlProStation = pd.DataFrame(columns=['Ort', 'Anzahl_Aufzüge'])

for i in uniquelist_orte:
    tmp = len(aufzüge[aufzüge['Ort'] == i])
    df_anzahlProStation.loc[i] = i,tmp
df_anzahlProStation = df_anzahlProStation.sort_values(by=['Anzahl_Aufzüge'], ascending=False)

####################################
######   Aggregierte Werte    ######
####################################

# Anzahl Antriebsart
anzahl_seilAufzüge = len(aufzüge[aufzüge['ANTRIEBSART'] == 'SEIL'])
anzahl_hydraulischAufzüge = len(aufzüge[aufzüge['ANTRIEBSART'] == 'HYDRAULISCH'])

# Top Hersteller
uniquelist_hersteller = aufzüge['Hersteller'].unique()

df_anzahlAufzüge = pd.DataFrame(columns=['Hersteller', 'Anzahl_Aufzüge'])

for i in uniquelist_hersteller:
    tmp = len(aufzüge[aufzüge['Hersteller'] == i])
    df_anzahlAufzüge.loc[i] = i,tmp
df_anzahlAufzüge = df_anzahlAufzüge.sort_values(by=['Anzahl_Aufzüge'], ascending=False)


# Aufälle gesamt
df_anzahlAusfälle = pd.DataFrame(columns=['Aufzug_ID', 'Anzahl_Ausfälle'])

temp_count = facilities.aggregate( [
    { '$match': { 'state': 'INACTIVE' } },
    {
        '$group': {
            '_id': "$equipmentnumber",
            'count': { '$sum': 1 }
        }
    }
] )

for i in temp_count:
    df_anzahlAusfälle.loc[i['_id']] = i['_id'], i['count']

df_anzahlAusfälle = df_anzahlAusfälle.sort_values(by=['Anzahl_Ausfälle'], ascending=False)

aufzug_aggregiert, anzahl_aggregiert = df_anzahlAusfälle['Aufzug_ID'].iloc[0], df_anzahlAusfälle['Anzahl_Ausfälle'].iloc[0]

###############################
###### Karte für Aufzüge ######
###############################

inactive, active, geolocator = createMap('ELEVATOR')


###################################
###### Karte für Rolltreppen ######
###################################

escalator_inactive, escalator_active, escalator_geolocator = createMap('ESCALATOR')

###################################
##### Daten für Rolltreppen  ######
###################################

graphDataEscalator = createGraphDataForEscalatorPage(14)


####################################
######        APP             ######
####################################

# Die Passworter eigentlich aus dem Quellcode-Repository heraushalten und in einer Datei oder einer Datenbank speichern.
VALID_USERNAME_PASSWORD_PAIRS = [
    ['Josh', '1234'],
    ['Sophie', '1234'],
    ['Phil', '1234'],
    ['Bart', '1234']
]
server = flask.Flask('EVA Dashboard')
app =  dash.Dash('EVA Dashboard', server=server)
app.title = 'EVA Dashboard'
auth = dash_auth.BasicAuth(
     app,
     VALID_USERNAME_PASSWORD_PAIRS
)

# Erklärung:
# Since we're adding callbacks to elements that don't exist in the app.layout, Dash will raise an exception to warn us
# that we might be doing something wrong. In this case, we're adding the elements through a callback, so we can ignore the exception.
app.config.suppress_callback_exceptions = True

###########################################################################################################
###########################################################################################################
#######################################                             #######################################
####################################### 2. Seite für Rolltreppen    #######################################
#######################################                             #######################################
###########################################################################################################
###########################################################################################################

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

page_rolltreppen = html.Div(children=[

    # Überschrift
    html.Div([
        html.H1(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center', 'width': '15em'},
                children='EVA Dashboard'),
    ]),

    # Unterüberschrift
    html.Div([
        html.Hr(),

        html.H1(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center', 'width': '15em',
                       'color': '#000099'}, children='Der Rolltreppenwärter'),
        dcc.Markdown('''
                **Informationen rund um Rolltreppen in Bahnhöfen der DB Station & Service AG**
                '''.replace('  ', ''), className='beschreibung',
                     containerProps={
                         'style': {'maxWidth': '650px', 'color': '#000099', 'margin-left': 'auto',
                                   'margin-right': 'auto', 'text-align': 'center'}})
    ]),

    html.Div([
        dcc.Link('Go to Page Aufzüge', href='/page_aufzuege')
    ], style={'text-align': 'left'}),

    # Hauptteil
    html.Div([
        # Diagramme
        html.Div([dcc.Graph(
            id='diagramm_status',
            figure={
                'data': [
                    {'x': ['aktiv', 'inaktiv', 'keine Information'],
                     'y': [escalatorStateCountACTIVE, escalatorStateCountINACTIVE, escalatorStateCountUNKNOWN],
                     'type': 'bar', 'name': 'Rolltreppen',
                     'marker': dict(color=['green', 'red', 'orange'])
                     },
                ],
                'layout': {
                    'title': 'Die Rolltreppen im Überblick',
                    'width': '35%',
                    'align': 'left'
                }
            }
        )], style={'width': '35%', 'text-align': 'left', 'display': 'inline-block', 'padding-top': 10,
                   'padding-left': 140, 'padding-bottom': 10}),

        html.Div([dcc.Graph(
            id='diagramm_inaktive',
            figure={
                'data': [
                    {'values': escalator_value_array, 'type': 'pie', 'name': 'GründeInaktivität',
                     'marker': dict(colors=['#DCDCDC', '#778899', '#C0C0C0']), 'labels': escalator_key_array
                     },
                ],
                'layout': {
                    'title': 'Gründe für Inaktivität',
                    'width': '35%',
                    'align': 'right'

                }
            }
        )],
            style={'width': '40%', 'text-align': 'right', 'display': 'inline-block', 'padding-left': 10,
                   'padding-bottom': 10}),

        html.Hr(),

        html.Div([dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=graphDataEscalator['Datum'],
                        y=graphDataEscalator['Anzahl_Ausfälle'],
                        name='Anzahl Ausfälle',
                        marker=go.Marker(
                            color='rgb(55, 83, 109)'
                        )
                    )
                ],

                layout=go.Layout(
                    title='Anzahl der Ausfälle von Rolltreppen auf Tagesebene',
                    showlegend=True,
                    legend=go.Legend(
                        x=0,
                        y=1.0
                    ),
                    margin=go.Margin(l=40, r=0, t=40, b=30)
                )
            ),
            style={'height': 300, 'width': 800},
            id='escalator_mid_graph'
        )], style={'width': '60%', 'text-align': 'left', 'display': 'inline-block', 'padding-top': 10,
                   'padding-left': 140, 'padding-bottom': 10}),

        html.Hr(),

        # unteres Drittel
        html.Div([
            # Titel
            html.Div([
                html.H3(style={'margin-right': 'auto', 'text-align': 'left',
                               'color': '#000099'},
                        children='Funktionieren die Rolltreppen an deiner Haltestelle? - Finde es heraus!'),
            ], style={'width': '60%', 'text-align': 'left', 'display': 'inline-block', 'padding-top': 10,
                      'padding-left': 140, 'padding-bottom': 10}),  ## neu vorher gar nichts

            # linker Teil ########################################## geändert alle ids + escalator
            html.Div([
                html.Div(['Stadt:  '],
                         style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='escalator_stadt_input', value='Frankfurt', type='text',
                          style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Div(['Bundesland:  '],
                         style={'margin-left': '15', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='escalator_bundesland_input', value='Hessen', type='text',
                          style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Br(), html.Br(),
                dcc.RadioItems(
                    id='escalator_radio_button',
                    options=[
                        {'label': 'Aktive Rolltreppen', 'value': 'aktiv'},
                        {'label': 'Inaktive Rolltreppen', 'value': 'inaktiv'},
                        {'label': ' Alle Rolltreppen', 'value': 'beide'}
                    ],
                    value='inaktiv', style={'margin-left': 10}
                ),
                html.Iframe(id='escalator_karte', srcDoc=open('./projekt/Maps/map_inactive_elevators.html', 'r').read(),
                            style={'width': '90%', 'height': '30em'})
            ], style={'width': '49%', 'display': 'inline-block'}),

            #style={'width': '60%', 'text-align': 'left', 'display': 'inline-block', 'padding-top': 10,
            #          'padding-left': 140, 'padding-bottom': 10}),

            ##########################################################################################################################################
            ##########################################################################################################################################
            ##########################################################################################################################################

            # rechter Teil
            html.Div([
                html.Br(), html.Br(),
                html.Div(['Rolltreppen-ID:  '],
                         style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='rolltreppe_id_input', type='text',
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
                        id='datatable-status-escalator',
                        selected_row_indices=[],
                        min_height=250
                    ),

                    html.Br(),
                ])

            ], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'})

            ##########################################################################################################################################
            ##########################################################################################################################################
            ##########################################################################################################################################


        ], style={'margin-left': '20'}),

    ], style={'background-color': '#E6E6FA'}),

    # Fußzeile
    html.Div([], style={'height': 70}),
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
                         'style': {'maxWidth': '650px', 'color': '#000000', 'margin-left': 'auto',
                                   'margin-right': 'auto', 'text-align': 'center'}})
    ], style={'height': 70}),

], style={'marginTop': '2%', 'marginLeft': '5%', 'marginRight': '5%'})

#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

page_aufzuege = html.Div(children=[

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
                **Informationen rund um Aufzüge in Bahnhöfen der DB Station & Service AG**
                '''.replace('  ', ''), className='beschreibung',
                         containerProps={
                             'style': {'maxWidth': '650px', 'color': '#000099', 'margin-left': 'auto',
                                       'margin-right': 'auto', 'text-align': 'center'}})
        ]),

        html.Div([
                dcc.Link('Go to Page Rolltreppen', href='/page-rolltreppen')
        ], style={'text-align':'right'}),

        # Hauptteil
        html.Div([

            #Diagramme
            html.Div([], style={'width':'10%', 'display': 'inline-block', 'vertical-align':'top'}),
            html.Div([
                html.Div([ dcc.Graph(
                id='diagramm_status',
                figure={
                    'data': [
                        {'x': ['aktiv', 'inaktiv', 'keine Information'], 'y': [elevatorStateCountACTIVE, elevatorStateCountINACTIVE, elevatorStateCountUNKNOWN], 'type': 'bar', 'name': 'Aufzüge',
                         'marker': dict(color=['green', 'red', 'orange'])
                         },
                    ],
                    'layout': {
                        'title': 'Die Aufzüge im Überblick',
                        'width': '35%',
                        'align': 'left'
                    }
                }
                )], style={'width': '40%', 'display': 'inline-block', 'padding-top': 10, 'padding-bottom': 10}),

                html.Div([ dcc.Graph(
                id='diagramm_inaktive',
                figure={
                    'data': [
                        {'values': elevator_value_array, 'type': 'pie', 'name': 'GründeInaktivität',
                         'marker': dict(colors=['#DCDCDC', '#778899', '#C0C0C0']), 'labels': elevator_key_array
                         },
                    ],
                    'layout': {
                        'title': 'Gründe für Inaktivität',
                        'width': '35%',
                        'align': 'right'
                    }
                }
                )],
                style={'width': '40%', 'display': 'inline-block', 'padding-left': 10, 'padding-bottom': 10}),
            ], style={'width':'90%', 'margin':'auto', 'display': 'inline-block', 'vertical-align':'top'}),
            html.Hr(),

        #mittleres Drittel: "Wusstest du schon?", aggregierte Werte etc.
        html.Div([]),
        html.Div([
            html.H3(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'right',
                            'color': '#000099'}, children='Wusstest du schon?'),
            html.Br(),
            html.Div('Der älteste Aufzug ist aus dem Jahr {} steht in: {}'.format(aeltesteAufzug_jahr, aeltesteAufzug_ort)),
            html.Div(id='aeltester_aufzug', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
            html.Div('Die Station mit den meisten Aufzügen ist: {} mit {} Aufzügen'.format(df_anzahlProStation['Ort'].iloc[0], df_anzahlProStation['Anzahl_Aufzüge'].iloc[0])),
            #count wie oft eine 'stationnumber' vorkommt, kann dann die mit den meisten dann einer Stadt zugeordnet werden?
            html.Div(id='meisten_aufzüge', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
            html.Div('Der Aufzug mit den meinste Ausfällen ist {} mit {} Ausfällen'.format(aufzug_aggregiert, anzahl_aggregiert)),
            #count wie oft 'inactive' im Status vorkommt
            html.Div(id='meiste_ausfälle', style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
            html.Br(),
        ], style={'display': 'inline-block', 'text-align': 'right', 'width': '45%', 'margin-right':20, 'vertical-align':'top'}),

        html.Hr(style={'width': 1, 'height': 200, 'display': 'inline-block'}),

        html.Div([
            html.H3(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'left',
                               'color': '#000099'}, children='Aggregierte Werte'),
            html.Div([
                html.Div('Antriebsart:'),
                html.Br(), html.Br(), html.Br(), html.Br(),
                html.Div('Top Hersteller:'),
                html.Br(),
            ], style={'display':'inline-block', 'width': '20%' }),
            html.Div([
                html.Div('HYDRAULISCH: {} Aufzüge'.format(anzahl_hydraulischAufzüge)),
                html.Div('SEIL: {} Aufzüge'.format(anzahl_seilAufzüge)),
                html.Br(), html.Br(), html.Br(),
                html.Div('{}: {} Aufzüge'.format(df_anzahlAufzüge['Hersteller'].iloc[0], df_anzahlAufzüge['Anzahl_Aufzüge'].iloc[0])),
                html.Div('{}: {} Aufzüge'.format(df_anzahlAufzüge['Hersteller'].iloc[1], df_anzahlAufzüge['Anzahl_Aufzüge'].iloc[1])),
                html.Div('{}: {} Aufzüge'.format(df_anzahlAufzüge['Hersteller'].iloc[2], df_anzahlAufzüge['Anzahl_Aufzüge'].iloc[2]))


            ], style={'display':'inline-block', 'width': '80%', 'vertical-align':'top'})


        ], style={'display': 'inline-block', 'text-align': 'left', 'width': '50%', 'margin-left':20, 'vertical-align':'top'}),

        html.Hr(),

        #unteres Drittel
        html.Div([
            #Titel
            html.Div([
                html.H3(style={'margin-right': 'auto', 'text-align': 'left',
                           'color': '#000099'}, children='Funktionieren die Aufzüge an deiner Haltestelle? - Finde es heraus!'),
            ]),

            #linker Teil
            html.Div([
                html.Div(['Stadt:  '], style={'margin-left': 'auto', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='stadt_input', value='Frankfurt', type='text', style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Div(['Bundesland:  '], style={'margin-left': '15', 'margin-right': 'auto', 'display': 'inline-block'}),
                dcc.Input(id='bundesland_input', value='Hessen', type='text', style={'margin-left': '5', 'margin-right': 'auto', 'display': 'inline-block'}),
                html.Br(), html.Br(),
                dcc.RadioItems(
                    id='radio_button',
                    options=[
                        {'label': 'Aktive Aufzüge', 'value': 'aktiv'},
                        {'label': 'Inaktive Aufzüge', 'value': 'inaktiv'},
                        {'label': ' Alle Aufzüge', 'value': 'beide'}
                    ],
                    value='inaktiv', style={'margin-left':10}
                ),
                html.Iframe(id='karte', srcDoc=open('./projekt/Maps/map_inactive_elevators.html', 'r').read(),
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
                        columns=['Datum_Uhrzeit', 'Status' , 'Erklärung des Status'],
                        editable=False,
                        row_selectable=False,
                        filterable=False,
                        sortable=False,
                        id='datatable-status-elevator',
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


# Callback Karte aktualisieren für Aufzüge
@app.callback(
    Output(component_id='karte', component_property='srcDoc'),
    [Input(component_id='stadt_input', component_property='value'),
     Input(component_id='bundesland_input', component_property='value'),
     Input(component_id='radio_button', component_property='value')]
)
def karte_aktualisieren(input_stadt, input_bland, radio_button):

    if radio_button == 'aktiv':
        try: 
            input_user = str(input_stadt + ', ' + input_bland + ', Deutschland')
            location = geolocator.geocode(input_user)

            m = folium.Map(location=[location.latitude,location.longitude], zoom_start=10)

            # TODO: Zeitmessung!
            for i, row in active.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: '+ str(row['equipmentnumber'])+ ' Beschreibung: '+ str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']], 
                                  popup = tmp,
                                 icon=folium.Icon(color='green', icon='info-sign')).add_to(m)

            m.save('./projekt/Maps/map_active_elevators.html')
            return open('./projekt/Maps/map_active_elevators.html', 'r').read()
        
        except:    
            return open('./projekt/Maps/map_active_elevators_FFM.html', 'r').read()

    elif radio_button == 'inaktiv':
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

            m.save('./projekt/Maps/map_inactive_elevators.html')
            return open('./projekt/Maps/map_inactive_elevators.html', 'r').read()
        
        except:    
            return open('./projekt/Maps/map_inactive_elevators_FFM.html', 'r').read()

    else:
        try: 
            input_user = str(input_stadt + ', ' + input_bland + ', Deutschland')
            location = geolocator.geocode(input_user)

            m = folium.Map(location=[location.latitude,location.longitude], zoom_start=10)

            for i, row in active.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: '+ str(row['equipmentnumber'])+ ' Beschreibung: '+ str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']], 
                                  popup = tmp,
                                 icon=folium.Icon(color='green', icon='info-sign')).add_to(m)
                    
            for i, row in inactive.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: '+ str(row['equipmentnumber'])+ ' Beschreibung: '+ str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']], 
                                  popup = tmp,
                                 icon=folium.Icon(color='red', icon='info-sign')).add_to(m)

            m.save('./projekt/Maps/map_both_elevators.html')
            return open('./projekt/Maps/map_both_elevators.html', 'r').read()
        
        except:    
            return open('./projekt/Maps/map_inactive_elevators_FFM.html', 'r').read()


######################################################################################################
# Callback Karte aktualisieren für Rolltreppen
@app.callback(
    Output(component_id='escalator_karte', component_property='srcDoc'),
    [Input(component_id='escalator_stadt_input', component_property='value'),
     Input(component_id='escalator_bundesland_input', component_property='value'),
     Input(component_id='escalator_radio_button', component_property='value')]
)
def karte_aktualisieren(input_stadt, input_bland, radio_button):
    if radio_button == 'aktiv':
        try:
            input_user = str(input_stadt + ', ' + input_bland + ', Deutschland')
            location = escalator_geolocator.geocode(input_user)

            m = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)

            for i, row in escalator_active.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: ' + str(row['equipmentnumber']) + ' Beschreibung: ' + str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']],
                                  popup=tmp,
                                  icon=folium.Icon(color='green', icon='info-sign')).add_to(m)

            m.save('./projekt/Maps/map_active_escalators.html')
            return open('./projekt/Maps/map_active_escalators.html', 'r').read()

        except:
            return open('./projekt/Maps/map_active_escalators_FFM.html', 'r').read()

    elif radio_button == 'inaktiv':
        try:
            input_user = str(input_stadt + ', ' + input_bland + ', Deutschland')
            location = escalator_geolocator.geocode(input_user)

            m = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)

            for i, row in escalator_inactive.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: ' + str(row['equipmentnumber']) + ' Beschreibung: ' + str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']],
                                  popup=tmp,
                                  icon=folium.Icon(color='red', icon='info-sign')).add_to(m)

            m.save('./projekt/Maps/map_inactive_escalators.html')
            return open('./projekt/Maps/map_inactive_escalators.html', 'r').read()

        except:
            return open('./projekt/Maps/map_inactive_escalators_FFM.html', 'r').read()

    else:
        try:
            input_user = str(input_stadt + ', ' + input_bland + ', Deutschland')
            location = escalator_geolocator.geocode(input_user)

            m = folium.Map(location=[location.latitude, location.longitude], zoom_start=10)

            for i, row in escalator_active.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: ' + str(row['equipmentnumber']) + ' Beschreibung: ' + str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']],
                                  popup=tmp,
                                  icon=folium.Icon(color='green', icon='info-sign')).add_to(m)

            for i, row in escalator_inactive.iterrows():
                if str(row['geocoordY']) == 'nan' or str(row['geocoordX']) == 'nan':
                    pass
                else:
                    tmp = str('ID: ' + str(row['equipmentnumber']) + ' Beschreibung: ' + str(row['description']))
                    folium.Marker([row['geocoordY'], row['geocoordX']],
                                  popup=tmp,
                                  icon=folium.Icon(color='red', icon='info-sign')).add_to(m)

            m.save('./projekt/Maps/map_both_escalators.html')
            return open('./projekt/Maps/map_both_escalators.html', 'r').read()

        except:
            return open('./projekt/Maps/map_inactive_escalators_FFM.html', 'r').read()
######################################################################################################

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
        attribute = aufzug['Hersteller'].values
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
        attribute = tmp3['Standort Equipment'].values
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
    Output(component_id='datatable-status-elevator', component_property='rows'),
    [Input(component_id='aufzug_id_input', component_property='value')]
)
def elevator_tabelle_aktualisieren(input_value):
    try:
        tabellen_input = facilities.find({"type": "ELEVATOR", "equipmentnumber": int(input_value)})
        tabellen_input = pd.DataFrame(list(tabellen_input))
        tabellen_input = tabellen_input[['datetime', 'state', 'stateExplanation']]
        status_tabelle = tabellen_input[::-1]
        status_tabelle.columns = ['Datum_Uhrzeit', 'Status', 'Erklärung des Status']

        return status_tabelle.to_dict('records')

    except:
        return [{}]


@app.callback(
    Output(component_id='datatable-status-escalator', component_property='rows'),
    [Input(component_id='rolltreppe_id_input', component_property='value')]
)
def escalator_tabelle_aktualisieren(input_value):
    try:
        tabellen_input = facilities.find({"type": "ESCALATOR", "equipmentnumber": int(input_value)})
        tabellen_input = pd.DataFrame(list(tabellen_input))
        tabellen_input = tabellen_input[['datetime', 'state', 'stateExplanation']]
        status_tabelle = tabellen_input[::-1]
        status_tabelle.columns = ['Datum_Uhrzeit', 'Status', 'Erklärung des Status']

        return status_tabelle.to_dict('records')

    except:
        return [{}]


#Seite updaten für den Wechsel zwischen Aufzügen und Rolltreppen
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-aufzuege':
        return page_aufzuege
    elif pathname == '/page-rolltreppen':
        return page_rolltreppen
    else:
        return page_aufzuege

if sys.version_info < (3, 0):
    sys.exit("Dieses Programm erfordert Python 3.0 und höher")

app.run_server(debug=False, host=HOST_ID, port=PORT)
