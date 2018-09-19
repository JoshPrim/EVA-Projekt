from project import db

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

class Elevator(db.Model):
    __tablename__ = 'elevator'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    standort_equipment = db.Column(db.String(128), nullable= True)
    technplatzbezeichng = db.Column(db.String(128), nullable= True)
    equipment = db.Column(db.Integer, nullable= True)
    equipmentname = db.Column(db.String(256), nullable= True)
    ort = db.Column(db.String(128), nullable= True)
    wirtschaftseinheit = db.Column(db.String(128), nullable= True)
    hersteller = db.Column(db.String(128), nullable= True)
    baujahr = db.Column(db.String(128), nullable= True)
    antriebsart = db.Column(db.String(128), nullable= True)
    anzahl_haltestellen = db.Column(db.String(128), nullable= True)
    anzahl_tueren_kabine = db.Column(db.String(128), nullable= True)
    anzahl_tueren_schacht = db.Column(db.String(128), nullable= True)
    foerdergeschwindigkeit = db.Column(db.String(128), nullable= True)
    foerderhoehe = db.Column(db.String(128), nullable= True)
    lage = db.Column(db.String(128), nullable= True)
    tragkraft = db.Column(db.String(128), nullable= True)
    erweiterte_ortsangabe = db.Column(db.String(128), nullable= True)
    min_tuerbreite = db.Column(db.String(128), nullable= True)
    kabinentiefe = db.Column(db.String(128), nullable= True)
    kabinenbreite = db.Column(db.String(128), nullable= True)
    kabinenhoehe = db.Column(db.String(128), nullable= True)
    tuerhohe = db.Column(db.String(128), nullable= True)
    fabriknummer = db.Column(db.String(128), nullable= True)
    tuerart = db.Column(db.String(128), nullable= True)
    geokoordinaterechtswert = db.Column(db.String(128), nullable = True)
    geokoordinatehochwert = db.Column(db.String(128), nullable = True)
    ausftextlichebeschreibung = db.Column(db.String(1280), nullable = True)

    def __init__(self,standort_equipment,technplatzbezeichng,equipment,equipmentname,ort,wirtschaftseinheit,hersteller,baujahr,antriebsart,anzahl_haltestellen,anzahl_tueren_kabine,anzahl_tueren_schacht,foerdergeschwindigkeit,foerderhoehe,lage,tragkraft,erweiterte_ortsangabe,min_tuerbreite,kabinentiefe,kabinenbreite,kabinenhoehe,tuerhohe,fabriknummer,tuerart,geokoordinaterechtswert, geokoordinatehochwert, ausftextlichebeschreibung ):
       self.standort_equipment = standort_equipment
       self.technplatzbezeichng = technplatzbezeichng
       self.equipment = equipment
       self.equipmentname = equipmentname
       self.ort = ort
       self.wirtschaftseinheit = wirtschaftseinheit
       self.hersteller = hersteller
       self.baujahr = baujahr
       self.antriebsart = antriebsart
       self.anzahl_haltestellen = anzahl_haltestellen
       self.anzahl_tueren_kabine = anzahl_tueren_kabine
       self.anzahl_tueren_schacht = anzahl_tueren_schacht
       self.foerdergeschwindigkeit = foerdergeschwindigkeit
       self.foerderhoehe = foerderhoehe
       self.lage = lage
       self.tragkraft = tragkraft
       self.erweiterte_ortsangabe = erweiterte_ortsangabe
       self.min_tuerbreite = min_tuerbreite
       self.kabinentiefe = kabinentiefe
       self.kabinenbreite = kabinenbreite
       self.kabinenhoehe = kabinenhoehe
       self.tuerhohe = tuerhohe
       self.fabriknummer = fabriknummer
       self.tuerart = tuerart
       self.geokoordinaterechtswert = geokoordinaterechtswert
       self.geokoordinatehochwert = geokoordinatehochwert
       self.ausftextlichebeschreibung = ausftextlichebeschreibung

    def to_json(self):
        return{
            'standort_equipment' :self.standort_equipment,
            'technplatzbezeichng' :self.technplatzbezeichng,
            'equipment' :self.equipment,
            'equipmentname' :self.equipmentname,
            'ort' :self.ort,
            'wirtschaftseinheit':self.wirtschaftseinheit,
            'hersteller':self.hersteller,
            'baujahr' :self.baujahr,
            'antriebsart' :self.antriebsart,
            'anzahl_haltestellen' :self.anzahl_haltestellen,
            'anzahl_tueren_kabine' :self.anzahl_tueren_kabine,
            'anzahl_tueren_schacht':self.anzahl_tueren_schacht,
            'foerdergeschwindigkeit':self.foerdergeschwindigkeit,
            'foerderhoehe' :self.foerderhoehe,
            'lage' :self.lage,
            'tragkraft' :self.tragkraft,
            'erweiterte_ortsangabe' :self.erweiterte_ortsangabe,
            'min_tuerbreite' :self.min_tuerbreite,
            'kabinentiefe':self.kabinentiefe,
            'kabinenbreite':self.kabinenbreite,
            'kabinenhoehe' :self.kabinenhoehe,
            'tuerhohe' :self.tuerhohe,
            'fabriknummer' :self.fabriknummer,
            'tuerart' :self.tuerart,
            'geokoordinaterechtswert':self.geokoordinaterechtswert,
            'geokoordinatehochwert' :self.geokoordinatehochwert,
            'ausftextlichebeschreibung':self.ausftextlichebeschreibung
        }























