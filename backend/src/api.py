import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import traceback

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/drinks')
def getDrinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })
    except:
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def getDrinkdetails(payload):
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createDrink(payload):
    try:
        body = request.get_json()
        drink = Drink(title=body['title'], recipe=json.dumps(body['recipe']))
        print(drink.long())
        drink.insert()
        print(2)
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except:
        traceback.print_exc()
        abort(422)


@app.route('/drinks/<drinkId>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updateDrink(payload,drinkId):
    
    drink = Drink.query.filter_by(id=drinkId).one_or_none()
    if not drink:
        abort(404)
    try:
        body = request.get_json()

        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])
        
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)

@app.route('/drinks/<drinkId>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrink(payload,drinkId):
    try:
        drink = Drink.query.filter_by(id=drinkId).one_or_none()

        if not drink:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drinkId
    })
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def notFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 422

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)
