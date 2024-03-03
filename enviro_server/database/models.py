from enviro_server.extensions import db

# Record model
class EnvironmentRecordModel(db.Model):
    __tablename__ = 'environment_record'
    query = db.session.query_property()
    id = db.Column(db.Integer, primary_key=True)
    ptime = db.Column(db.DateTime)
    value = db.Column(db.Float, nullable=False, unique=False)
    field_name = db.Column(db.String(50), nullable=False, unique=False)
    unit = db.Column(db.String(50), db.ForeignKey('environment_units.type'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'ptime': self.ptime,
            'value': self.value,
            'field_name': self.field_name,
            'unit': self.unit,
        }


# Environment unit model
class EnvironmentUnitModel(db.Model):
    __tablename__ = 'environment_units'
    type = db.Column(db.String(50), primary_key=True)
    unit = db.Column(db.String(10), nullable=False, unique=False)
    records = db.relationship('EnvironmentRecordModel', backref='environment_units', lazy=True)

# User model
class User(db.Model):
    nickname = db.Column(db.String(50), primary_key=True)
    full_name = db.Column(db.String(100))
    password = db.Column(db.String(100))