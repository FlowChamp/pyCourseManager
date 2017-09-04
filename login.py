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

def requires_login(func):
    def try_token(*args, **kwargs):
        authorized = False

        uname = kwargs['user']
        school = kwargs['school']
        username = f"{school}-{uname}"

        user = User.query.filter_by(username=username).first()
        # Some sanity checks on the user
        if not user:
            abort(404, message=f"User {uname} not found with the selected institution")
        if user.is_expired():
            abort(403, message="Api key expired, please reauthenticate")

        token = request.cookies.get('friday-login-token')
        api_key = request.headers.get('x-api-key')

        if token is not None:
            authorized = user.check_token(token)
        elif api_key:
            authorized = user.check_token(api_key)
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

    def __init__(self, username, token):
        self.username = username
        self.set_token(token)

    def set_token(self, token):
        self.token = generate_password_hash(token)
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
    """Send a GET request to the API to authenticate the user. If the user 
    authentication succeeds, give the client a grant token"""
    def get(self, school):
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
        if result != "DENY":
            cookie = resp.cookies['org.jasig.portal.PORTLET_COOKIE']
            token = hashlib.sha256(str.encode(cookie)).hexdigest()

            username = f"{school}-{username}"

            tmp_user = User.query.filter_by(username=username).first()
            if tmp_user is not None:
                tmp_user.set_token(token)
            else: 
                user = User(username, token)
                db.session.add(user)

            db.session.commit()
            
            utc_time = datetime.utcnow() + timedelta(minutes=30)
            date = utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

            return {"token": token}, {'Set-Cookie': f'friday-login-token={token};Expires={date}'}
        else:
            abort(401, message=f"Password incorrect for {username}")

    def post(self, school):
        self.get(school)


