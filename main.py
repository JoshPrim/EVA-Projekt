#'''
# Autor: Joshua Prim, Philipp Krenitz, Bartos Mosch, Sophie Hagemann
# Version: 1.0
#
# Dieses Programm mappt die Stammmdaten auf die Facilities und speichert sie in die MongoDB.
#
# Copyright 2018 The Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==============================================================================
#
#'''
#
#from pprint import pprint
#import pandas as pd
#import json
#import csv
#import sys
#
#sys.path.append('./Clients')
#
#from Python_Client import FaSta_Request
#from Postgres_Client import PostgreSQL_Zugriff
#
#class ReferFacilitiesToStations():
#
#    def __init__(self):
#        self.postgres_server_url = 'my-development-at.my-router.de'
#        self.postgres_server_user = 'eva-user'
#        self.postgres_server_passwort = 'downy37tory'
#        self.postgres_server_database = 'postgres'
#
#        self.api_key = 'd16d67e35458c895f557696799eb4e8f'
#
#        try:
#            #{2736: 'Hervest-Dorsten', 599: 'Beucha', 473: 'Belleben', 222: 'Augsburg Morellstraße', 3337: 'Köln-Nippes', ...}
#            stammdaten_ziehen = PostgreSQL_Zugriff(self.postgres_server_url, self.postgres_server_user, self.postgres_server_passwort, self.postgres_server_database)
#            self.csv_reader = stammdaten_ziehen.zugriff()
#
#        except Exception as e:
#            print(e)
#            print('Fehler Stammdaten Laden!')
#
#
#    def getFacilities(self):
#
#        columns = ['Stationnumber', 'Name', 'Facilities']
#
#        self.pandasDF = pd.DataFrame(columns=columns)
#        self.listWithFacilities = []
#        self.fastaFacilities_Liste = []
#
#        # FaSta API Zugriff
#        api_zugriff = FaSta_Request(self.api_key)
#        self.fastaFacilities_Liste = api_zugriff.request()
#
#        def dataCleaningForSorting(json):
#
#            return json['stationnumber']
#
#        self.fastaFacilities_Liste = sorted(self.fastaFacilities_Liste, key=dataCleaningForSorting)     # sortiert, weil stationnumber 3 aus json vorkommt, dann datensatz mit stationnumber 4 und dann wieder ein datensatz mit stationnumber 3 kommt --> er fängt zwei listen an
#        self.rownum = 0
#
#        for key, value in self.csv_reader.items(): # Über jeden Datensatz in der eingelesenen CSV-Datei iterieren
#
#            if self.rownum == 0:
#                self.rownum = self.rownum + 1
#                continue
#
#            temp_facilities = str()
#            self.rownum = self.rownum + 1
#
#            for i in range(len(self.fastaFacilities_Liste)):     # Über jeden Datensatz in der eingelesenen JSON-Datei iterieren
#
#                if i == 0:
#                    temp_facilities = str(self.fastaFacilities_Liste[i]['stationnumber'])            # Speichere erstes Element, die die Zuweisung erst im zweiten Durchlauf automatisiert am Ende geschieht
#
#                if (str(key) == str(self.fastaFacilities_Liste[i]['stationnumber']) and temp_facilities == str(self.fastaFacilities_Liste[i]['stationnumber'])):       # Zwei Überprüfungen: 1) Stimmt "Bh. Nr." aus CSV mit "stationnumber" aus JSON überein, 2) Stimmt Stationnumber des letzten Eintrags mit der "momentanen" übereinstimmt
#                    self.listWithFacilities.append(self.fastaFacilities_Liste[i])                                # übereinstimmender JSON-Datensatz wird an eine Liste zur Zwischenspeicherung angehangen
#
#                if not (str(key) == str(self.fastaFacilities_Liste[i]['stationnumber']) and temp_facilities == str(self.fastaFacilities_Liste[i]['stationnumber'])):   # Gegenteil zu den "Zwei Überprüfungen" ein if weiter oben
#                    if (bool(self.listWithFacilities) == True):                     # Wenn es keine Übereinstimmung mit dem CSV- und JSON-Datensatz gab --> leere Liste --> hier muss sie jedoch mind. einen Eintrag enthalten
#
#                        data = {'Stationnumber': key, 'Name': value, 'Facilities': self.listWithFacilities}
#                        self.pandasDF = self.pandasDF.append(data, ignore_index=True)
#
#                        self.listWithFacilities = []                                # Liste wird für nächsten Durchlauf wieder geleert
#
#                temp_facilities = str(self.fastaFacilities_Liste[i]['stationnumber'])    # Für nächsten Durchlauf zum Vergleich auf Übereinstimmungen zwischengespeichert
#
#        return self.pandasDF
#
#
#if __name__ == '__main__':
#
#
#    instanceof_ReferFacilitiesToStations = ReferFacilitiesToStations()
#    df = instanceof_ReferFacilitiesToStations.getFacilities()
#
#    print('Matched Table: ', df)
#
#    # Speichern der Json in die MongoDB
#    '''
#    conn = pymongo.MongoClient("mongodb://lcalehost")
#    db = conn.book
#    record1 = db.book_collection
#
#    for item in r.json():
#        record1.insert(item)
#    '''
#

import threading
import time
from pprint import pprint
from Version.Python_Client import FaSta_Request
import json
import pymongo

def main():

    while True:
        t = threading.Thread(target=printer())
        t.start

def printer():
 while True:

    client = pymongo.MongoClient('mongodb://bart:downy37)tory@my-development-at.my-router.de:27777/eva')
    dbeva = client.eva
    facilities = dbeva.facilities

    #print("hello world")
    request  = FaSta_Request('d16d67e35458c895f557696799eb4e8f').request()

    for api_item in range( len (request)):

     try:
         print("api_item equipmentnumber")
         print(request[api_item]["equipmentnumber"])

         search_result = dbeva.facilities.find({"equipmentnumber": request[api_item]["equipmentnumber"]}).sort([("datetime",pymongo.DESCENDING)])

         print("mongo db count")
         print(search_result.count())

         if( search_result.count() > 0 ):

          print("facility found")
          for mongo_item in search_result:
                  if( mongo_item["state"] != request[api_item]["state"] ):
                   print(mongo_item)
                   print("")
                   print("mongoitem state:")
                   print(mongo_item["state"])

                   print("")
                   print("api_item state:")
                   print(request[api_item]["state"])

                   print("status has changed! - Inserting update!")

                   facilities.insert_one(request[api_item])
                   break


         else:
              print("facility not found -> initial inserting")
              facilities.insert_one(request[api_item])
              print(" ")

     except Exception as e:
            print(e)
            print('Fehler beim Request!')

   # for item in request:
    #    facilities.insert(item)

    #pprint(request)
    #result = json.loads(request)
    #print(json.dumps(result, indent=4))

    time.sleep(60)



if __name__ == "__main__":
    main()