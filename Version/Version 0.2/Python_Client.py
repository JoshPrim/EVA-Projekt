'''
 Autor: Joshua Prim, Philipp Krenitz, Bartos Mosch, Sophie Hagemann
 Version: 1.0

 Dieses Programm stellt den Client für die FaSta-Api der Deutschen Bahn dar.

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

import requests
import json
import datetime
import time
import os
import pymongo

class FaSta_Request():

    def __init__(self, api_key):
        self.api_key = 'Bearer ' + api_key
    

    def request(self):
        print('Zugriff wird ausgeführt!')

        # Verzeichnis zum lokalen Speichern de Json anlegen
        def create_log_directories():
            date_n_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
            logdir = './Logs/{}/'.format(date_n_time)

            if not os.path.exists(os.path.abspath('./Logs')):
                os.mkdir(os.path.abspath('./Logs'))

            if not os.path.exists(os.path.abspath(logdir)):
                os.makedirs(os.path.abspath(logdir))
                print('Verzeichnis erstellt:', logdir)
            return logdir

        self.logdir = create_log_directories()
        

        # Request an die FaSta API
        try:
            url = 'https://api.deutschebahn.com/fasta/v2/facilities?type=ELEVATOR'
            headers = {'Accept': 'application/json' , 'Authorization': self.api_key}

            r = requests.get(url, headers=headers)
            print('Request Status Code: ', r.status_code)
            #print('Request Json: ', r.json())

            # Json als .json abspeichern
            with open(self.logdir + 'FaSta.json', 'w') as outfile:
                json.dump(r.json(), outfile)

            # Json als .txt abspeichern
            with open(self.logdir + 'FaSta.txt', 'w') as outfile:
                json.dump(r.json(), outfile)

            print('Zurgiff erfolgreich abgeschlossen!')

            return r.json()
    
            
        except Exception as e:
            print(e)
            print('Fehler beim Request!')


