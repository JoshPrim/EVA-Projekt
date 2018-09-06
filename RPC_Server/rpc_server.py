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


class MyService(rpyc.Service):
    def exposed_anzahlAusfälle(self):
        return df_anzahlAusfälle['Aufzug_ID'].iloc[0], df_anzahlAusfälle['Anzahl_Ausfälle'].iloc[0]



# Timer ist auf 03:00 Uhr morgens gestellt und löst täglich aus
def timer():
    x=datetime.today()
    y=x.replace(day=x.day+1, hour=3, minute=0, second=0, microsecond=0)
    delta_t=y-x
    return delta_t.seconds+1

def run():
    resultDictionary = {}
    client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva')
    dbeva = client.eva
    facilities = dbeva['facilities']

    # Liste alles Aufzug IDs
    aufzug_ID_liste = facilities.distinct("equipmentnumber")

    # Start der Zeitmessung
    start_time = time.time()

    global df_anzahlAusfälle
    
    for aufzug_ID in aufzug_ID_liste:
        
        tabellen_input = facilities.find({"type": "ELEVATOR", "equipmentnumber": aufzug_ID})
        tabellen_input = pd.DataFrame(list(tabellen_input))

        if tabellen_input.empty:
            pass
        else:
            tabellen_input = tabellen_input[['datetime', 'state']]
            status_tabelle = tabellen_input[::-1]
            status_tabelle.columns = ['Datum_Uhrzeit', 'Status']
            tmp = status_tabelle.to_dict('records')

            counter = 0
            for i in tmp:
                if i['Status'] == 'INACTIVE':
                    counter += 1
            df_anzahlAusfälle.loc[aufzug_ID] = aufzug_ID, counter
            df_anzahlAusfälle = df_anzahlAusfälle.sort_values(by=['Anzahl_Ausfälle'], ascending=False)

    print("---Die Prozedur dauerte %s Sekunden ---" % (time.time() - start_time))


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
