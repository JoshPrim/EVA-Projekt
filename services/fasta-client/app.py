import threading
import time
from pprint import pprint
import json
import pymongo
import os
from project.api.FaSta_Client import FaSta_Request

def startRequests():
    while True:
        mongo_uri = os.getenv('MONGO_URL')
        print(mongo_uri)
        client = pymongo.MongoClient(os.getenv(mongo_uri))

        dbeva = client.eva
        facilities = dbeva.facilities

        # print("hello world")
        request =   FaSta_Request('d16d67e35458c895f557696799eb4e8f').getFacilites()

        for api_item in range(len(request)):

            try:
                print("api_item equipmentnumber")
                print(request[api_item]["equipmentnumber"])

                search_result = dbeva.facilities.find({"equipmentnumber": request[api_item]["equipmentnumber"]}).sort(
                    [("datetime", pymongo.DESCENDING)]).limit(1)

                print("mongo db count")
                print(search_result.count())

                if (search_result.count() > 0):

                    print("facility found")
                    for mongo_item in search_result:
                        if (mongo_item["state"] != request[api_item]["state"]):
                            print("")
                            print("mongo_item:")
                            print(mongo_item)
                            print("")
                            print("mongo_item state:")
                            print(mongo_item["state"])

                            print("")
                            print("api_item")
                            print(request[api_item])
                            print("")
                            print("api_item state:")
                            print(request[api_item]["state"])
                            print(request[api_item])

                            print("status has changed! - Inserting update!")
                            print("inserting:")
                            print(request[api_item])
                            # facilities.insert_one(request[api_item])
                        break

                else:
                    print("facility not found -> initial inserting")
                    # facilities.insert_one(request[api_item])
                    print(" ")

            except Exception as e:
                print(e)
                print('Fehler beim Request!')

        # for item in request:
        #    facilities.insert(item)

        # pprint(request)
        # result = json.loads(request)
        # print(json.dumps(result, indent=4))

        time.sleep(60)


if __name__ == "__main__":
    startRequests()