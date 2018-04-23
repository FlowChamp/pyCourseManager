import os, hashlib, json 
import requests
from flask import request
from flask_restful import Resource, abort
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import lxml.html

db = SQLAlchemy()

def check_config_init(client, username):
    if username not in client.database_names():
        if client[username].config.count() == 1:
            return

        config = {
            "username": username,
            "start_year": 0,
            "active_chart": "",
            "charts": {}
        }
        client[username].config.insert_one(config)

def requires_login(func):
    def try_token(*args, **kwargs):
        authorized = False

        uname = kwargs['user']
        school = kwargs['school']
        username = f"{school}-{uname}"

        user = User.query.filter_by(username=username).first()
        # Some sanity checks on the user
        if not user:
            abort(404, message=f"User {uname} not found. Is the user logged in?")
        if user.is_expired():
            abort(403, message="Api key expired, please reauthenticate")

        token = request.cookies.get('friday-login-token')

        if token:
            authorized = user.check_token(token)
        else:
            abort(400, message="No authorization token found. Is the user logged in?")

        if not authorized:
            abort(401, message=f"User {uname} is not authorized for the requested endpoint")

        return func(*args, **kwargs)

    return try_token      

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    token = db.Column(db.String(80))
    token_expiration = db.Column(db.DateTime())

    def __init__(self, username, token, remember=None):
        self.username = username
        self.set_token(token, remember)

    def set_token(self, token, remember=None):
        self.token = generate_password_hash(token)
        if remember:
            self.token_expiration = datetime.now() + timedelta(days=365)
        else:
            self.token_expiration = datetime.now() + timedelta(minutes=30)

    def check_token(self, tk):
        return check_password_hash(self.token, tk) 
    
    def is_expired(self):
        return datetime.now() > self.token_expiration

    def __str__(self):
        return f"{self.username}: {self.token}"
    def __repr__(self):
        return '<User %r>' % self.username

class AuthorizeResource(Resource):
    def __init__(self, client):
        self.client = client

    """Send a GET request to the API to authenticate the user. If the user 
    authentication succeeds, give the client a grant token"""
    def get(self, school):
        args = request.get_json()
        username = request.authorization.username
        password = request.authorization.password

        params = {'service': "https://myportal.calpoly.edu/Login"}
        LOGIN = "https://my.calpoly.edu/cas/login"
        session = requests.session()

        login = session.get(LOGIN, params=params)
        login_html = lxml.html.fromstring(login.text)
        hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
        form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}

        form['username'] = username 
        form['password'] = password 

        resp = session.post(LOGIN, data=form, params=params)

        result = resp.headers['X-Frame-Options']

        print(resp.cookies)
        cookie = resp.cookies['org.jasig.portal.PORTLET_COOKIE']
        abort(400, message="This is not the login you are looking for")

        token = hashlib.sha256(str.encode(cookie)).hexdigest()

        username = f"{school}-{username}"
        if args:
            rem = True if args.get("remember") else False
        else:
            rem = False

        tmp_user = User.query.filter_by(username=username).first()
        if tmp_user is not None:
            tmp_user.set_token(token, remember=rem)
        else: 
            user = User(username, token, remember=rem)
            db.session.add(user)

        db.session.commit()
        
        check_config_init(self.client, username) 
        config = self.client[username].config.find_one()
        del config['_id']
        
        utc_time = datetime.utcnow() 
        utc_time += timedelta(days=365) if rem else timedelta(minutes=30)
        date = utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

        return config, {'Set-Cookie': f'friday-login-token={token};Expires={date}'}
        # else:
            # abort(401, message=f"Password incorrect for {username}")

    def post(self, school):
        return self.get(school)

class LogoutResource(Resource):
    @requires_login
    def post(self, school, user):
        # requires_login ensures that there will be a user before we get here
        username = f"{school}-{user}"
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()

        return {"message": f"User {user} successfully logged out"}

