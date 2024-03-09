#import datetime
from json import load
from enviro_server.database.models import EnvironmentRecordModel
from enviro_server.EnvironmentData import EnvironmentData, EnvironmentValue, Limits, Units

def load_environment_data(resource_path):
    with open(resource_path, "r") as resource:
        dict_data = load(resource)
        _raw_data = dict_data
        _data = [EnvironmentRecordModel(id=entry["id"], ptime=entry["ptime"],
                                                value=entry["value"], field_name=entry["field_name"],
                                                unit=entry["unit"])
                        for entry in dict_data]
        return (_raw_data, _data)