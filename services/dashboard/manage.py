# services/users/manage.py


from flask.cli import FlaskGroup
from project import app, db
import unittest
import os

cli = FlaskGroup(app)


@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    #load_data()

@cli.command()
def load_data():
    """ Load station master data from csv"""
    with open(os.environ.get('MASTER_DATA'),  'r') as f:
        conn = db.create_engine('postgresql+psycopg2://postgres:postgres@station-db:5432/station_dev').raw_connection()
        cursor = conn.cursor()
        cmd = 'COPY station(bundesland,rb,bm,bfNr,station,bfDs100Abk,katVst,strasse,plz,ort,aufgabenvergeber) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)'
        #cmd = '\ dt'
        cursor.copy_expert(cmd, f)
        conn.commit()


if __name__ == '__main__':
    cli()


