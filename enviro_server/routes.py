from flask import jsonify, abort, request,  Response
from flask.views import View
from enviro_server.tasks import app
from flask_cors import cross_origin

# Flask endpoints to read data from database 
@app.route("/test", methods=["GET"])
@cross_origin(origin='*')
def get_entries():
    response = jsonify({"result": "ok"})
    return response, 200