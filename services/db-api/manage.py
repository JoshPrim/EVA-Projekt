# services/db-api/project/manage.py


from flask.cli import FlaskGroup, with_appcontext
from project import app, db, mongo
from project.api_models.station import Station
import os

cli = FlaskGroup(app)

@cli.command()
def recreate_db():
    print('Running cli_recreate_db')
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def init_tables():
    print('Running through cli_init_tables')
    """ Load station master data from csv"""
    with open(os.environ.get('MASTER_STATION'), 'r') as f:
        conn = db.engine.connect().connection
        cursor = conn.cursor()
        cmd = 'COPY station(bundesland,rb,bm,bfnr,station,bfdsabk,katvst,strasse,plz,ort,aufgabenvergeber) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ";", ENCODING "UTF-8")'
        cursor.copy_expert(cmd, f)
        conn.commit()

    with open(os.environ.get('MASTER_ELEVATOR'), 'r') as f:
        conn = db.engine.connect().connection
        cursor = conn.cursor()
        cmd = 'COPY elevator(standort_equipment,technplatzbezeichng,equipment,equipmentname,ort,wirtschaftseinheit,hersteller,baujahr,antriebsart,anzahl_haltestellen,anzahl_tueren_kabine,anzahl_tueren_schacht,foerdergeschwindigkeit,foerderhoehe,lage,tragkraft,erweiterte_ortsangabe,min_tuerbreite,kabinentiefe,kabinenbreite,kabinenhoehe,tuerhohe,fabriknummer,tuerart,geokoordinaterechtswert,geokoordinatehochwert,ausftextlichebeschreibung) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ";", ENCODING "UTF-8")'
        cursor.copy_expert(cmd, f)
        conn.commit()

#mongo cli commands
@cli.command()
def mongo_init():
   print('run trough docker with: docker-compose exec mongo-db mongorestore -u bart -p "downy37)tory" -h mongo-db --port 27017 -d eva_dev  ./data/db/dump/eva')
   #mongo.cx.admin.command('ismaster')


if __name__ == '__main__':
    print('Running through main')
    cli()
