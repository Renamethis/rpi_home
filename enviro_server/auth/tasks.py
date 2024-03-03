from werkzeug.security import generate_password_hash, check_password_hash

from enviro_server.extensions import celery, db
from enviro_server.database.models import User

@celery.task()
def signup_task(args):
    request = args[0]
    nickname = request.form.get('nickname')
    full_name = request.form.get('full_name')
    password = request.form.get('password')

    user = User.query.filter_by(nickname=nickname).first()

    if user:
        return None

    new_user = User(nickname=nickname, full_name=full_name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return new_user