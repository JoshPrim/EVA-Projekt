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
                  print(mongo_item)
                  if( mongo_item["state"] != request[api_item]["state"] ):

                   print("status has changed! - Inserting update!")
                   facilities.insert_one(api_item)
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

    time.sleep(30)



if __name__ == "__main__":
    main()