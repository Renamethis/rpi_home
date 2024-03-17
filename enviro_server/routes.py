import os
from flask import request
from enviro_server import app
from enviro_server.tasks import last_entries, current_state, by_date, load_weather
from flask_cors import cross_origin

# Return data assigned to specific date
@app.route("/find_by_date/<date>")
@cross_origin(origin='*')
def find_by_date(date):
    return by_date.delay([request.headers.get("Authorization"), app.config["SECRET_KEY"], date]).get(), 200

# Read last 30 entries of EnvrionmentRecord from database
@app.route("/get_last_entries/<pointer>/<amount>", methods=["GET"])
@cross_origin(origin='*')
def get_last_entries(pointer, amount):
    return last_entries.delay([request.headers.get("Authorization"), app.config["SECRET_KEY"], int(pointer), int(amount),]).get(), 200

@app.route("/get_current_state", methods=["GET"])
@cross_origin(origin='*')
def get_current_indicators():
    return current_state.delay([request.headers.get("Authorization"), app.config["SECRET_KEY"]]).get(), 200

@app.route("/load_weather/<lattitude>/<longitude>", methods=["GET"])
@cross_origin(origin='*')
def get_current_weather(lattitude, longitude):
    result = load_weather.delay([request.headers.get("Authorization"), app.config["SECRET_KEY"], lattitude, longitude]).get()
    return result[0], int(result[1])