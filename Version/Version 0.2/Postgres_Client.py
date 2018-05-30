'''
 Autor: Joshua Prim, Philipp Krenitz, Bartos Mosch, Sophie Hagemann
 Version: 1.0

 Dieses Programm stellt den Client für die Verbindung zu einer PostgreSQL Datenbank dar.

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

import psycopg2
import pgdb

class PostgreSQL_Zugriff(object):

    def __init__(self, hostname, username, password, database):
        self.hostname = hostname 
        self.username = username 
        self.password = password 
        self.database = database

    # Routine, um eine Abfrage auf einer Datenbank auszuführen
    def doQuery(self, conn) :
        cur = conn.cursor()
        
        querry = 'SELECT DISTINCT "Bf. Nr.", Station FROM station' 
        cur.execute( querry )

        stammdaten_liste = {}

        for bf_Nr, station in cur.fetchall() :
            stammdaten_liste[bf_Nr] = station

        return stammdaten_liste

    def zugriff(self):
        try:
            verbindung = psycopg2.connect( host=self.hostname, user=self.username, password=self.password, dbname=self.database, port=54134 )
            stammdaten_dict = self.doQuery( verbindung )
            verbindung.close()
            '''
            verbindung = pgdb.connect( host=self.hostname, user=self.username, password=self.password, database=self.database )
            stammdaten_dict = doQuery( verbindung )
            verbindung.close()
            '''
            return stammdaten_dict
            
        except  Exception as e:
            print(e)
            print('Fehler beim Request!')

        return False

'''
if __name__ == '__main__':
    stammdaten_ziehen = PostgreSQL_Zugriff('my-development-at.my-router.de', 'eva-user', 'downy37tory', 'postgres')
    stammdaten = stammdaten_ziehen.zugriff()

    print(stammdaten)
'''

