
import json
import objdict
from objdict import ObjDict

fac_dummy = [
  {
    "equipmentnumber": 10499641,
    "type": "ELEVATOR",
    "description": "zu Gleis 1",
    "geocoordX": 14.6713589,
    "geocoordY": 51.0993991,
    "state": "ACTIVE",
    "stateExplanation": "available",
    "stationnumber": 3751
  },
  {
    "equipmentnumber": 10499641,
    "type": "ELEVATOR",
    "description": "zu Gleis 1",
    "geocoordX": 14.6713589,
    "geocoordY": 51.0993991,
    "state": "INACTIVE",
    "stateExplanation": "not available",
    "stationnumber": 3751
  },
{
    "equipmentnumber": 10499642,
    "type": "ELEVATOR",
    "description": "zu Gleis 2/3",
    "geocoordX": 14.6713245,
    "geocoordY": 51.0995518,
    "state": "ACTIVE",
    "stateExplanation": "available",
    "stationnumber": 3751
  },
]

fac_json_dummy = json.dumps(fac_dummy)


station_dict = ObjDict({
  "stationnumber": 3751,
  "name": "Löbau (Sachs)",
  "facilities": [
   {
     "equipmentnumber": 10499641,
     "latest_timestamp": "2018-05-15_14-02-01",
     "type": "ELEVATOR",
     "description": "zu Gleis 1",
     "geocoordX": 14.6713589,
     "geocoordY": 51.0993991,
     "state": [
     	{"datetime":"2018-05-15_14-02-01", "value": "ACTIVE"},
     	{"datetime":"2018-05-15_14-01-53", "value": "UNKOWN"},
     	{"datetime":"2018-05-15_14-01-26", "value": "INACTIVE"}
     ],
     "stateExplanation": [
     	{"datetime":"2018-05-15_14-02-01", "value": "available"},
     	{"datetime":"2018-05-15_14-01-53", "value": "monitoring disrupted"},
     	{"datetime":"2018-05-15_14-01-26", "value": "not available"}
     ],
     "stationnumber": 3751
   }
  ]
}
)

object2 = ObjDict({
  "stationnumber": 9999,
  "name": "Mond",
  "facilities": [
   {
     "equipmentnumber": 999999,
     "latest_timestamp": "2018-05-15_14-02-01",
     "type": "ELEVATOR",
     "description": "zu Gleis 1",
     "geocoordX": 14.6713589,
     "geocoordY": 51.0993991,
     "state": [
     	{"datetime":"2018-05-15_14-02-01", "value": "ACTIVE"},
     	{"datetime":"2018-05-15_14-01-53", "value": "UNKOWN"},
     	{"datetime":"2018-05-15_14-01-26", "value": "INACTIVE"}
     ],
     "stateExplanation": [
     	{"datetime":"2018-05-15_14-02-01", "value": "available"},
     	{"datetime":"2018-05-15_14-01-53", "value": "monitoring disrupted"},
     	{"datetime":"2018-05-15_14-01-26", "value": "not available"}
     ],
     "stationnumber": 3751
   }
  ]
}
)


'{"stationnumber": 9999,"name": "Mond","facilities": {"equipmentnumber": 999999,"latest_timestamp": "2018-05-15_14-02-01","type": "ELEVATOR","description": "zu Gleis 1","geocoordX": 14.6713589,"geocoordY": 51.0993991,"state": [	{"datetime":"2018-05-15_14-02-01", "value": "ACTIVE"},{"datetime":"2018-05-15_14-01-53", "value": "UNKOWN"},{"datetime":"2018-05-15_14-01-26", "value": "INACTIVE"}],"stateExplanation":[{"datetime":"2018-05-15_14-02-01", "value": "available"},	{"datetime":"2018-05-15_14-01-53", "value": "monitoring disrupted"},	{"datetime":"2018-05-15_14-01-26", "value": "not available"}],"stationnumber": 3751}]}'