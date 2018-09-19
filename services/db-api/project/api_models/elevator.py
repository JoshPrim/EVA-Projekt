from flask import jsonify
from project.api_models.models import Elevator
from project import app

# routes
@app.route('/elevators', methods=['GET'])
def get_all_elevator():
    response_object = {
        'status': 'success',
        'data': {
            'elevator': [elevator.to_json() for elevator in Elevator.query.all()]
        }
    }
    return jsonify(response_object), 200
