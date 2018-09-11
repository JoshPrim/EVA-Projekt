from project import db, mongo

# postgres models
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

# classes & routes mongo ## NUR MIT mongoengine Implementierung
#class Facility(mongo.db.Document):
#    equipmentnumber = mongo.db.StringField(required=False)
#    type = mongo.db.StringField(required=False)
#    description = mongo.db.StringField(required=False)
#    geocoordX = mongo.db.StringField(required=False)
#    geocoordY = mongo.db.StringField(required=False)
#    state = mongo.db.StringField(required=False)
#    stateExplanation = mongo.db.StringField(required=False)
#    stationnumber = mongo.db.StringField(required=False)
#
#    def __init__(self,equipmentnumber,type,description,geocoordX,geocoordY,state,stateExplanation,stationnumber):
#       self.equipmentnumber = equipmentnumber
#       self.type = type
#       self.description  = description
#       self.geocoordX  = geocoordX
#       self.geocoordY  = geocoordY
#       self.state  = state
#       self.stateExplanation = stateExplanation
#       self.stationnumber = stationnumber
#
#    def to_json(self):
#        return {
#          'equipmentnumber': self.equipmentnumber,
#          'type': self.type,
#          'description': self.description ,
#          'geocoordX': self.geocoordX ,
#          'geocoordY': self.geocoordY ,
#          'state': self.state ,
#          'stateExplanation': self.stateExplanation,
#          'stationnumber': self.stationnumber
#        }

