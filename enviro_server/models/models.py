from enviro_server.extensions import db

# Environment data model
class EnvironmentDataModel(db.Model):
    __tablename__ = 'environment_data'
    query = db.session.query_property()
    ptime = db.Column(db.DateTime, primary_key=True)
    temperature = db.Column(db.Float, nullable=False, unique=False)
    humidity = db.Column(db.Float, nullable=False, unique=False)
    pressure = db.Column(db.Float, nullable=False, unique=False)
    illumination = db.Column(db.Float, nullable=False, unique=False)
    reducing = db.Column(db.Float, nullable=False, unique=False)
    oxidising = db.Column(db.Float, nullable=False, unique=False)
    nh3 = db.Column(db.Float, nullable=False, unique=False)
        
class EnvironmentUnits(db.Model):
    __tablename__ = 'environment_units'
    field_name = db.Column(db.String(50), primary_key=True)
    unit = db.Column(db.String(10), primary_key=True)