from flask import jsonify, abort, request,  Response
from flask.views import View
from enviro_server.tasks import app, last_entries, current_state, by_date
from enviro_server.database.models import EnvironmentRecordModel, EnvironmentUnitModel
from flask_cors import cross_origin


# Return data assigned to specific date
@app.route("/find_by_date/<date>")
@cross_origin(origin='*')
def find_by_date(date):
    return by_date.delay([date,]).get(), 200

# Read last 30 entries of EnvrionmentRecord from database
@app.route("/get_last_entries/<amount>", methods=["GET"])
@cross_origin(origin='*')
def get_last_entries(amount):
    return last_entries.delay([int(amount),]).get(), 200

@app.route("/get_current_indicators", methods=["GET"])
@cross_origin(origin='*')
def get_current_indicators():
    return current_state.delay().get(), 200