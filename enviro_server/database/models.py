import jwt
import datetime
from enviro_server.extensions import db
from werkzeug.security import generate_password_hash

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

# Blacklist model
class Blacklist(db.Model):
    __tablename__ = 'blacklist'

    token = db.Column(db.String(500), primary_key=True, unique=True, nullable=False)
    join_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.join_date = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token, session):
        res = session.query(Blacklist).filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

# User model
class User(db.Model):
    __tablename__ = "users"
    nickname = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(100))
    registered_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, nickname, password, admin=False):
        self.nickname = nickname
        self.password = generate_password_hash(password, method='sha256')
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    @staticmethod
    def decode_auth_token(secret, auth_token, session):
        try:
            payload = jwt.decode(auth_token, secret, algorithms="HS256")
            is_blacklisted_token = Blacklist.check_blacklist(auth_token, session)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.', 1
            else:
                return payload['sub'], 0
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 1
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 1

    def encode_auth_token(self, secret, validity=datetime.timedelta(days=1)):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + validity,
                'iat': datetime.datetime.utcnow(),
                'sub': self.nickname
            }
            return jwt.encode(
                payload,
                secret,
                algorithm='HS256'
            )
        except Exception as e:
            return str(e)
