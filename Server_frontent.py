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

# -*- coding: utf-8 -*-


import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
import dash_auth


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
                html.H1(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center', 'width': '15em'},
                        children='EVA Dashboard'),
            ]),

            # Beschreibung
            html.Div([
                html.H2(style={'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center', 'width': '10em',
                               'color': '#000099'}, children='Der Aufzugwächter'),
                dcc.Markdown('''
                    Informationen rund um Aufzuege und Rolltreppen in Bahnhöfen der DB Station & Service AG
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
                        {'x': ['aktiv', 'inaktiv', 'keine Information'], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Aufzüge',
                         'marker': dict(color=['green', 'red', 'grey'])
                         },
                    ],
                    'layout': {
                        'title': 'Die Aufzüge im Überblick',
                        'width': '35%',
                        'align': 'left'

                    }
                }
                )], style={'width': '35%', 'text-align': 'left', 'display': 'inline-block', 'padding-top': 10, 'padding-left': 140, 'padding-bottom': 10 }),

                html.Div([dcc.Graph(
                id='diagramm_inaktive',
                figure={
                    'data': [
                        {'x': ['aktiv', 'inaktiv', 'keine Information'], 'y': [2, 3, 5], 'type': 'bar',
                         'name': 'Aufzüge'},
                    ],
                    'layout': {
                        'title': 'Gründe für Inaktivität',

                    }
                }
                )], style={'width': '40%', 'text-align': 'right', 'display': 'inline-block', 'padding-left': 10, 'padding-bottom': 10}),

            ], style = {'background-color': '#F0F8FF'}
            )



        ], style={'marginTop': '2%', 'marginLeft': '5%', 'marginRight': '5%'})


        ##########################################################################           #############################################################################################################################################
        ########################################################################## CALLBACKS #############################################################################################################################################
        ##########################################################################           #############################################################################################################################################

        # @app.callback():

        # app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

        app.run_server(debug=False, host='0.0.0.0', port='37001')


if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.run()
