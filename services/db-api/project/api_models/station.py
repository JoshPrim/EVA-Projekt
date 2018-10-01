from flask import jsonify
from project.api_models.models import Station
from project import app

# routes
@app.route('/station/all', methods=['GET'])
def get_all_stations():
    response_object = {
        'status': 'success',
        'data': {
            'station': [station.to_json() for station in Station.query.all()]
        }
    }
    return jsonify(response_object), 200
