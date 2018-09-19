# services/users/app.py


from flask.cli import FlaskGroup
from project import app, db, mongo
from project.api_models.station import Station
import os

cli = FlaskGroup(app)

@cli.command()
def recreate_db():
    print("inside recreate_db")
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def load_data():
    init_db()

def init_db():
    """ Load station master data from csv"""
    with open(os.environ.get('MASTER_STATION'),  'r') as f:
        conn = db.create_engine('postgresql+psycopg2://postgres:postgres@station-db:5432/eva_dev').raw_connection()
        cursor = conn.cursor()
        cmd = 'COPY station(bundesland,rb,bm,bfnr,station,bfdsabk,katvst,strasse,plz,ort,aufgabenvergeber) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ";")'
        cursor.copy_expert(cmd, f)
        conn.commit()

    with open(os.environ.get('MASTER_ELEVATOR'), 'r') as f:
        conn = db.create_engine('postgresql+psycopg2://postgres:postgres@station-db:5432/eva_dev').raw_connection()
        cursor = conn.cursor()
        cmd = 'COPY elevator(standort_equipment,technplatzbezeichng,equipment,equipmentname,ort,wirtschaftseinheit,hersteller,baujahr,antriebsart,anzahl_haltestellen,anzahl_tueren_kabine,anzahl_tueren_schacht,foerdergeschwindigkeit,foerderhoehe,lage,tragkraft,erweiterte_ortsangabe,min_tuerbreite,kabinentiefe,kabinenbreite,kabinenhoehe,tuerhohe,fabriknummer,tuerart,geokoordinaterechtswert,geokoordinatehochwert,ausftextlichebeschreibung) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ";")'
        cursor.copy_expert(cmd, f)
        conn.commit()

#mongo cli commands
@cli.command()
def mongo_init():
   mongo.cx.admin.command('ismaster')


if __name__ == '__main__':
    db.create_all()
    init_db()
    cli()
