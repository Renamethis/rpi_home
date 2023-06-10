from enviro_server.extensions import db

# Record model
class RecordModel(db.Model):
    __tablename__ = 'environment_data'
    query = db.session.query_property()
    ptime = db.Column(db.DateTime, primary_key=True)
    value = db.Column(db.Float, nullable=False, unique=False)
    field_name = db.Column(db.String(50), db.ForeignKey('environment_units.field_name'), nullable=False)

# Environment unit model
class EnvironmentUnitModel(db.Model):
    __tablename__ = 'environment_units'
    field_name = db.Column(db.String(50), primary_key=True)
    unit = db.Column(db.String(10), primary_key=True, nullable=False, unique=False)
    records = db.relationship('RecordModel', backref='environment_units', lazy=True)