from . import app, db
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
    RoleMixin, login_required

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(80), unique=True)
    description = db.Column(db.Unicode(255))


class User(db.Model, UserMixin):
    # Columns required by flask-security
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    # columns required by SECURITY_TRACKABLE
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer())
    confirmed_at = db.Column(db.DateTime())

    # columns used by us specifically
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    home_phone = db.Column(db.String(50))
    cell_phone = db.Column(db.String(50))
    emergency_contact_phone = db.Column(db.String(50))
    emergency_contact_name = db.Column(db.String(255))
    birthday = db.Column(db.Date())

    created_at = db.Column(db.DateTime(), server_default=db.func.now())

    address = db.Column(db.String(50))
    address2 = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(7))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
