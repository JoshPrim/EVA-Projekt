from collections import OrderedDict
from pprint import pprint
import json
import csv
#from objdict import ObjDict

class StationInJson():

    def __init__(self, path):

        self.path = path

    def getDict(self):

        result = {}

        try:

            file = open(self.path, "r", encoding='utf-8')
            csv_reader = csv.reader(file, delimiter=";")

            rownum = 0

            for row in csv_reader:

                if rownum == 0:

                    next(csv_reader)
                    rownum = rownum + 1

                else:

                    result[row[3]] = row[4]
                    rownum = rownum + 1

            #pprint(result)
            #pprint('#####')
            #pprint(result['95'])
            #pprint(result['991'])

            file.close()

            return result

        except Exception as e:

            print(e)
            print('Fehler beim Einlesen der CSV! Hat Ihre Datei keinen Header oder ist es keine CSV-Datei?')


    def csvToJson(self):

        result = self.getDict()
        jsonObject = {}

        try:

            counter = 0

            for row in result:

                #pprint(result)
                jsonObject[int(row)] = result[row]

                counter += 1

##############################
            #for k, v in result.items():

                #print('K: ' + k)
                #print('V: ' + v)

            json_dict = OrderedDict([
                ('stationnumber', int(k)),
                ('name', str(v))
            ] for k, v in result.items())

            '''
            ('facilities', [OrderedDict([
                    (''),
                    (''),
                    ('')
                ])
            '''

            '''
            json_dict = OrderedDict([
                ('stationnumber', 'abc.pdf'),
                ('name', ''),
                ('data', [OrderedDict([
                    ('keyword', k),
                    ('term_freq', len(v)),
                    ('lists', [{'occurrance': i} for i in v])
                ]) for k, v in dic.iteritems()])
            ])
            '''

            '''
            with open('abc.json', 'w') as outfile:
                json.dump(json_dict, outfile)

            # Now to read the orderer json file

            with open('abc.json', 'r') as handle:
                new_json_dict = json.load(handle, object_pairs_hook=OrderedDict)
                print(json.dumps(json_dict, indent=4))
            '''

            #erg = json.dumps(json_dict)
            #print(erg)
            #jsonObject = json.dumps(jsonObject)
##############################
            return jsonObject
            #return json_dict
            #return erg

        except Exception as e:

           print(e)
           print('Fehler beim Einlesen der CSV! Hat Ihre Datei keinen Header oder ist es keine CSV-Datei?')


if __name__ == '__main__':

    path = "C:/Users/Philipp/Documents/-- Master --/1. Semester/Entwicklung verteilter Systeme/DBSuS-Uebersicht_Bahnhoefe-Stand2018-03.csv"

    stationInJson = StationInJson(path)

    result = stationInJson.getDict()

    #pprint(result['987'])
    #pprint(result['6902'])

    jsonObject = stationInJson.csvToJson()
    pprint(jsonObject)

    '''
        import json

        with open('C:/Users/Philipp/Documents/-- Master --/1. Semester/Entwicklung verteilter Systeme/FaSta.json') as json_data:
            fastaFacilities_Liste = json.load(json_data)
            json_data.close()
            #pprint(fastaFacilities_Liste)

            for index in range(len(fastaFacilities_Liste)):
            ''#pprint(fastaFacilities_Liste[index]['stationnumber'])
    '''