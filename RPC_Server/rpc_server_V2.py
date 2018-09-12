# -*- coding: utf-8 -*-

import pandas as pd
from pandas import DataFrame
import numpy as np

import pymongo
import collections
from pprint import pprint
from pymongo.command_cursor import CommandCursor
import types

import time
from datetime import datetime
from threading import Timer
import rpyc
from rpyc.utils.server import ThreadedServer


df_anzahlAusfälle = pd.DataFrame(columns=['Aufzug_ID', 'Anzahl_Ausfälle'])
ergDF = pd.DataFrame(columns=['Datum', 'Anzahl_Ausfälle'])

class MyService(rpyc.Service):
    def exposed_anzahlAusfälle(self):
        return df_anzahlAusfälle['Aufzug_ID'].iloc[0], df_anzahlAusfälle['Anzahl_Ausfälle'].iloc[0]

    def exposed_createEscalatorGraph(self):
        return ergDF



# Timer ist auf 03:00 Uhr morgens gestellt und löst täglich aus
def timer():
    x=datetime.today()
    y=x.replace(day=x.day+1, hour=3, minute=0, second=0, microsecond=0)
    delta_t=y-x
    return delta_t.seconds+1

def run():
    client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva')
    dbeva = client.eva
    facilities = dbeva['facilities']

    # Start der Zeitmessung
    start_time = time.time()

    global df_anzahlAusfälle
    
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
    
    
    print("---Die Prozedur dauerte %s Sekunden ---" % (time.time() - start_time))

    ##########################################################################################################
    try:

        global ergDF

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

        ergDF = ergDF.iloc[-14:]

        ergDF = ergDF.reset_index().drop(['index'], axis=1)

    except Exception as e:
        print(e)



def runScheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(run, 'interval', hours=24)
    scheduler.start()


if __name__ == "__main__":
    # Initialisierung
    print('Initalbefüllung gestartet ...')
    run()
    print('Initalbefüllung abgeschlossen')
    

    # Start der Dautenaufbereitung
    trigger = timer()
    t = Timer(trigger, runScheduler)
    t.start()
    print('Datenaufbereitungsthread erfolgreich gestartet')

    print('Start des RPC Servers: localhost:37005')
    server = ThreadedServer(MyService, port = 37005)
    server.start()
