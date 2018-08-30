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
    bfNr = db.Column(db.Integer)
    station = db.Column(db.String(128), nullable=False)
    bfDs100Abk = db.Column(db.String(10), nullable=False)
    katVst = db.Column(db.Integer, nullable=False)
    strasse = db.Column(db.String(128), nullable=False)
    plz = db.Column(db.Integer, nullable=False)
    ort  = db.Column(db.String(128), nullable=False)
    aufgabenvergeber = db.Column(db.String(128), nullable=False)


    def __init__(self, bundesland, rb, bm , bfNr, station, bfDs100Abk, katVst, strasse, plz, ort, aufgabenvergeber):
        self.bundesland = bundesland
        self.rb = rb
        self.bm = bm
        self.bfNr =  bfNr
        self.station = station
        self.bfDs100Abk = bfDs100Abk
        self.katVst =  katVst
        self.strasse = strasse
        self.plz = plz
        self.ort = ort
        self.aufgabenvergeber = aufgabenvergeber


# routes
@app.route('/station/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
