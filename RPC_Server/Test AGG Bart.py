import pymongo
import collections
from pprint import pprint
from pymongo.command_cursor import CommandCursor
import types

import time
from datetime import datetime

start_time = time.time()

resultDictionary = {}
client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva')
dbeva = client.eva
facilities = dbeva['facilities']

tmp = facilities.aggregate( [
    { '$match': { 'state': 'INACTIVE' } },
    {
        '$group': {
            '_id': "$equipmentnumber",
            'count': { '$sum': 1 }
        }
    }
] )

print("--- %s seconds ---" % (time.time() - start_time))

# Ausgeben lassen
#for i in tmp:
    #print(i)

