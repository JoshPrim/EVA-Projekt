import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# instantiate the db
db = SQLAlchemy(app)

# model
class Station(db.Model):
    """
    Bundesland: Bundesland, z.B. Hessen.
    RB: Bezeichnung Regionalbereich, z.B. RB Mitte
    BM: Bahnhofsmanagement, z.B. Darmstadt.
    Bf.Nr.: Eindeutige Nr. des Bahnhofs, z.B. 119.
    Station: Name der Station, z.B. Altheim (Hess).
    Bf DS 100 Abk.: Verweis auf Betriebsstelle, z.B. FAT.
    Kat. Vst.: Bahnhofskategorie, z.B. 6.
    Straße: Postalische Adressinfo.
    PLZ: Postalische Adressinfo.
    Ort: Postalische Adressinfo.
    """
    __tablename__ = 'station'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bundesland = db.Column(db.String(128), nullable=False)
    rb = db.Column(db.String(128), nullable=False)
    bm = db.Column(db.String(128), nullable=False)
    bfnr = db.Column(db.Integer, nullable=False)
    station = db.Column(db.String(128), nullable=False)
    bfdsabk = db.Column(db.String(10), nullable=False)
    katvst = db.Column(db.Integer, nullable=False)
    strasse = db.Column(db.String(128), nullable=True)
    plz = db.Column(db.Integer, nullable=True)
    ort  = db.Column(db.String(128), nullable=True)
    aufgabenvergeber = db.Column(db.String(128), nullable=True)


    def __init__(self, bundesland, rb, bm , bfnr, station, bfdsabk, katvst, strasse, plz, ort, aufgabenvergeber):
        self.bundesland = bundesland
        self.rb = rb
        self.bm = bm
        self.bfnr =  bfnr
        self.station = station
        self.bfdsabk = bfdsabk
        self.katvst =  katvst
        self.strasse = strasse
        self.plz = plz
        self.ort = ort
        self.aufgabenvergeber = aufgabenvergeber

    def to_json(self):
        return {
          'bundesland':self.bundesland,
          'rb':self.rb,
          'bm':self.bm,
          'bfnr':self.bfnr,
          'station':self.station,
          'bfdsabk':self.bfdsabk,
          'katvst':self.katvst,
          'strasse':self.strasse,
          'plz':self.plz,
          'ort':self.ort,
          'aufgabenvergeber':self.aufgabenvergeber
        }


# routes
@app.route('/station/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

# routes
@app.route('/station', methods=['GET'])
def get_all_stations():
    response_object = {
        'status': 'success',
        'data': {
            'station': [station.to_json() for station in Station.query.all()]
        }
    }
    return jsonify(response_object), 200