from flask import jsonify, abort, request,  Response
from flask.views import View
from enviro_server.tasks import app, last_entries
from enviro_server.database.models import EnvironmentRecordModel, EnvironmentUnitModel
from flask_cors import cross_origin

MAX_LAST_ENTRIES = 30

# Read last 30 entries of EnvrionmentRecord from database
@app.route("/get_last_entries", methods=["GET"])
@cross_origin(origin='*')
def get_last_entries():
    return last_entries.delay().get(), 200