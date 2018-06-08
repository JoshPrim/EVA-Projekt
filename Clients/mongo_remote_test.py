from __future__ import print_function
import pymongo
import json

client = pymongo.MongoClient('mongodb://bart:downy37)tory@my-development-at.my-router.de:27777/eva')
dbeva = client.eva
facilities = dbeva.facilities

fac_json_string = '{"equipmentnumber": 99999,"type": "ELEVATOR", "description": "zu Gleis 1","geocoordX": 14.6713589,"geocoordY": 51.0993991,"state": "ACTIVE","stateExplanation": "available","stationnumber": 3751}'
json_obj_active = json.loads(fac_json_string)

fac_json_string = '{"equipmentnumber": 999999,"type": "ELEVATOR", "description": "zu Gleis 1","geocoordX": 14.6713589,"geocoordY": 51.0993991,"state": "INACTIVE","stateExplanation": "available","stationnumber": 3751}'
json_obj_inactive = json.loads(fac_json_string)

#for fac_json_obj in fac_json_array:
#    value = json.loads(fac_json_obj)
#    print(value)
#pass
import datetime
import time
date_n_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')



dbeva.facilities.insert(json_obj_active)


search_result = dbeva.facilities.find({"equipmentnumber": json_obj_active["equipmentnumber"]})
#search_result = dbeva.facilities.find()
for doc in search_result:
          print(doc)

search_result = dbeva.facilities.find({"equipmentnumber": 10316334}).sort([("datetime",pymongo.DESCENDING)])
#search_result = dbeva.facilities.find()
print(search_result.count())

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