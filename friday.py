import json, os, sqlalchemy
from datetime import datetime, timedelta 
from OpenSSL import SSL 

from course_manager import CourseManager

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource, abort
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.provider import OAuth2Provider

app = Flask(__name__)
api = Api(app)
CORS(app)

db = SQLAlchemy(app)
oauth = OAuth2Provider(app)

app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:////srv/pyflowchart/users.db',
    SQLALCHEMY_TRACK_MODIFICATIONS = True,
    SECRET_KEY = 'secret_xxx'
)

today = datetime.today()

fall = datetime(today.year, 9, 15)
winter = datetime(today.year, 1, 1)
spring = datetime(today.year, 3, 31)
summer = datetime(today.year, 6, 15)

if fall <= today <= datetime(today.year, 12, 31):
    quarter = 0
elif winter <= today < spring:
    quarter = 1
elif spring <= today < summer:
    quarter = 2
else:
    quarter = 3

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_password(self, pw):
        return pw == self.password

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 

    def __repr__(self):
        return '<User %r>' % self.username

class Client(db.Model):
    name = db.Column(db.String(40))
    description = db.Column(db.String(400))
    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')

    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True,
                              nullable=False)

    is_confidential = db.Column(db.Boolean)
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
    
    def as_dict(self):
        return {"client_id": self.client_id, "code": self.code}

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()

@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()

@oauth.grantsetter
def save_grant(user, client_id, code, scopes, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code,
        _scopes=scopes,
        user=User.query.filter_by(username=user).first(),
        expires=expires 
    )
    db.session.add(grant)
    db.session.commit()
    return grant

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    user = User.query.filter_by(username=username).first()
    if user.check_password(password):
        return user
    return None

@oauth.tokengetter
def get_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    if refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()
    return None 

# /useradd 
class NewUserResource(Resource):
    def post(self):
        print("Here")
        try:
            data = request.get_json()
            print(data)
            username = data['username']
            password = data['password']

            if not password: 
                abort(401, message=f"Please provide password for {username} in the 'api-key' header")
            
            db.session.add(User(username, password))
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            abort(409, message=f"User {username} already exists")

# /authorize 
class LoginResource(Resource):
    """Send a POST request to the API to authenticate the user. If the user 
    authentication succeeds, give the client a grant token"""
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        ip = request.remote_addr
        client_id = f"{username}@{ip}"

        if db.session.query(User.username).filter_by(username=username).scalar is None: 
            abort(404, message=f"User {username} does not exist")

        if not password:
            abort(401, message=f"Please provide password for {username}")

        user = get_user(username, password) 
        if user:
            new_client = Client(name=client_id, client_id=client_id, 
                _redirect_uris=('http://devjimheald.com:4500/authorized'))
            grant = save_grant(username, client_id, 'steelcowboy', username)
            return grant.as_dict()

        else:
            abort(401, message=f"Password incorrect for {username}")

# /oauth/authorize
class OauthResource(Resource):
    @oauth.authorize_handler
    def post(self):
        # First check if the client has the correct grant
        data = request.get_json()
        grant = load_grant(data['client_id'], data['code'])
        return get_token(grant) 

# /logout
class LogoutResource(Resource):
    @oauth.revoke_handler
    def post(self):
        logout_user()

# Login resources
api.add_resource(LoginResource,   '/authorize')
api.add_resource(NewUserResource, '/useradd')
# api.add_resource(LogoutResource,  '/logout')

api.add_resource(CourseManager.UsageResource,   '/')
api.add_resource(CourseManager.ListStockCharts, '/stock_charts')
api.add_resource(CourseManager.ListUserCharts,  '/<string:user>/charts')
api.add_resource(CourseManager.GetStockChart,   '/stock_charts/<string:major>')
api.add_resource(CourseManager.ChartResource,   '/<string:user>/charts/<string:chart>')
api.add_resource(CourseManager.CourseResource,  '/<string:user>/charts/<string:chart>/<int:c_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)

