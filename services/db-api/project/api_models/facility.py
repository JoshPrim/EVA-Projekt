from flask import jsonify, render_template
from project import app, mongo
import socket

# mongo  routes
@app.route('/mongo/get_all', methods=['GET'])
def get_all_fac():
    fac = mongo.db.facilities
    f = fac.find()
    output = []
    for f in f:
        output.append({
            'datetime': f['datetime'],
            'equipmentnumber' : f['equipmentnumber'],
            'type' : f['type'],
            'description' : f['description'],
            'geocoordX' : f['geocoordX'],
            'geocoordY' : f['geocoordY'],
            'state' : f['state'],
            'stateExplanation' : f['stateExplanation'],
            'stationnumber' : f['stationnumber']
        })

    response_object = {
        'status': 'success',
        'data': {
            'facility': output
        }
    }
    return jsonify((response_object), 200)


@app.route('/mongo/single', methods=['GET'])
def get_one_fac():
    fac = mongo.db.facilities
    f = fac.find_one({'equipmentnumber': 10499641})
    output = []
    output.append({'equipmentnumber': f['equipmentnumber']})
    response_object = {
        'status': 'success',
        'data': {
            'facility': output
        }
    }
    return jsonify((response_object))

@app.route('/mongo/count' )
def get_one_faci():
    count = mongo.db.facilities.count()
    return render_template('index.html',
    count=count, hostname=socket.gethostname())

# routes
@app.route('/mongo/agg', methods=['GET'])
def aggFac():
    f = mongo.db.facilities.aggregate( [
    { '$match': { 'state': 'INACTIVE' } },
    {
        '$group': {
            '_id': "$equipmentnumber",
            'count': { '$sum': 1 }
        }
    }
    ])
    output = []
    for f in f:
        output.append({
            '_id': f['_id'],
            'count' : f['count']
        })

    response_object = {
        'status': 'success',
        'data': {
            'facility': output
        }
    }
    return jsonify((response_object), 200)

# routes
@app.route('/mongo/ping', methods=['GET'])
def mongo_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

