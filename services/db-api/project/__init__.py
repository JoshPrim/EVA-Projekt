# services/db-api/project/__init__.py

import os
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo

print('Running through init')

app = Flask(__name__, template_folder='./templates')

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# instantiate the db, mongo

db = SQLAlchemy(app)
mongo = PyMongo(app)

#importing routes from facility
from project.api_models import facility
from project.api_models import elevator

# routes
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })