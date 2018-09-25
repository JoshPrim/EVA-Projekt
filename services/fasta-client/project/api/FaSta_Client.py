import requests
import json
import datetime
import time
import os

class FaSta_Request():

    def __init__(self, api_key):
        app_settings = os.getenv('APP_SETTINGS')
        self.api_key = 'Bearer ' + api_key
        self.FASTA_URL = os.getenv('FASTA_URL')
        self.LOG_DIR = os.getenv('LOG_DIR')

    def create_log_directories(self):
        #  date_n_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        if not os.path.exists(os.path.abspath(self.LOG_DIR)):
            os.mkdir(os.path.abspath(self.LOG_DIR))

        if not os.path.exists(os.path.abspath(self.LOG_DIR)):
            os.makedirs(os.path.abspath(self.LOG_DIR))
            print('Verzeichnis erstellt:', self.LOG_DIR)
        return self.LOG_DIR

    def getFacilites(self):
        print('Zugriff wird ausgeführt!')

        #self.logdir = self.create_log_directories()

        # Request an die FaSta API
        try:
            url = self.FASTA_URL
            print(url)
            headers = {'Accept': 'application/json', 'Authorization': self.api_key}

            response = requests.get(url, headers=headers)
            print('Request Status Code: ', response.status_code)
            # print('Request Json: ', r.json())
            date_n_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')

            # Json als .json abspeichern
            #with open(self.logdir + '{}.json'.format(date_n_time), 'w') as outfile:
            #    json.dump(response.json(), outfile)

            # Json als .txt abspeichern
            # with open(self.logdir + '{}.txt'.format(date_n_time), 'w') as outfile:
            #     json.dump(r.json(), outfile)

            print('Zurgiff erfolgreich abgeschlossen!')
            print(date_n_time)

            json_response = response.json()

            for i in range(len(json_response)):
                json_response[i]["datetime"] = date_n_time

            #print(json_response)

            return json_response


        except Exception as e:
            print(e)
            print('Fehler beim Request!')

