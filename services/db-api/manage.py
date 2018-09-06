# services/users/app.py


from flask.cli import FlaskGroup
from project import app, db
import unittest
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
    with open(os.environ.get('MASTER_DATA'),  'r') as f:
        conn = db.create_engine('postgresql+psycopg2://postgres:postgres@station-db:5432/station_dev').raw_connection()
        cursor = conn.cursor()
        cmd = 'COPY station(bundesland,rb,bm,bfnr,station,bfdsabk,katvst,strasse,plz,ort,aufgabenvergeber) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ";")'
        cursor.copy_expert(cmd, f)
        conn.commit()

if __name__ == '__main__':
    db.create_all()
    init_db()
    cli()
