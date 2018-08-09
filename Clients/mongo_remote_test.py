from __future__ import print_function
import pymongo
import json

client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva')
dbeva = client.eva
facilities = dbeva.facilities

search_result = dbeva.facilities.find()
print(search_result.count())

facilities = dbeva.facilities

client = pymongo.MongoClient('mongodb://bart:downy37)tory@localhost:27017/eva')
dbeva = client.eva
facilities = dbeva.facilities

fac_json_string = '{"equipmentnumber": 99999,"type": "ELEVATOR", "description": "zu Gleis 1","geocoordX": 14.6713589,"geocoordY": 51.0993991,"state": "ACTIVE","stateExplanation": "available","stationnumber": 3751}'
json_obj_active = json.loads(fac_json_string)

fac_json_string = '{"equipmentnumber": 10038566, "type": "ELEVATOR", "description": "zu Gleis 1/2", "geocoordX": 11.0592875, "geocoordY": 50.14624, "state": "ACTIVE", "stateExplanation": "available", "stationnumber": 3700, "datetime": "2018-06-08_18-24-48"}}'
json_obj_inactive = json.loads(fac_json_string)

#for fac_json_obj in fac_json_array:
#    value = json.loads(fac_json_obj)
#    print(value)
#pass
import datetime
import time
date_n_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')



dbeva.facilities.insert(json_obj_active)


search_result = dbeva.facilities.find({"type": "ESCALATOR"})
#search_result = dbeva.facilities.find()
for doc in search_result:
          print(doc)

search_result = dbeva.facilities.distinct({"equipmentnumber": 10463734}).sort([("datetime",pymongo.DESCENDING)])
#search_result = dbeva.facilities.find()
print(search_result.count())

# Gibt all equipemnts aus die mehr als einen Eintrag besitzen
search_result = dbeva.facilities.distinct("equipmentnumber")
for i in search_result:
    equip = dbeva.facilities.find({"equipmentnumber": i }).sort([("datetime", pymongo.DESCENDING)])
    if(equip.count() > 1):
     for y in equip:
         print(y)


if (search_result["state"] != fac_json_string["state"]):
    print("true")
#.sort("equipmentnumber")

for doc in search_result:
          print(doc)

for mongo_item in search_result:
 if( mongo_item["state"] != json_obj_active["state"] ):
  print("true")
 else:
  print("false")

dbeva.facilities.remove({})

# Close connection
print('Closing nt connection')
client.close()

#"10499642_2018-06-08_11-03-11"