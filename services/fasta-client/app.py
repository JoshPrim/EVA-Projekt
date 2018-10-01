import threading
import time
from pprint import pprint
import json
import pymongo
import os
from project.api.FaSta_Client import FaSta_Request

def startRequests():

    mongo_uri = os.getenv('MONGO_URI')
    API_KEY = 'd16d67e35458c895f557696799eb4e8f'

    while True:
        client = pymongo.MongoClient(mongo_uri)
        db = client.eva_dev
        facilities = db.facilities

        request = FaSta_Request(API_KEY).getFacilites()

        if  len(request) > 0 :
           for api_item in range(len(request)):

               try:
                   print("api_item equipmentnumber")
                   print(request[api_item]["equipmentnumber"])

                   search_result = db.facilities.find({"equipmentnumber": request[api_item]["equipmentnumber"]}).sort(
                       [("datetime", pymongo.DESCENDING)]).limit(1)

                   print("mongo db count")
                   #print(search_result.count())

                   if (search_result.count() > 0):

                       print("facility found")
                       for mongo_item in search_result:
                           if (mongo_item["state"] != request[api_item]["state"]):
                               print("mongo_item: ", mongo_item)
                               print("mongo_item state: ", mongo_item["state"])
                               print("api_item: ", request[api_item])

                               print("api_item state:")
                               print(request[api_item]["state"])
                               print(request[api_item])

                               print("status has changed! - Inserting update!")
                               print("inserting:")
                               print(request[api_item])
                               facilities.insert_one(request[api_item])
                           break
                   else:
                       print("facility not found -> initial inserting")
                       facilities.insert_one(request[api_item])

               except Exception as e:
                   print(e)
                   print('Fehler beim Mongo Request!')

        time.sleep(60)

if __name__ == "__main__":
    startRequests()
