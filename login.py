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
        return datetime.now() > self.api_key_expiration

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
            # expiry = resp.cookies['sessionExpiry']
            token = hashlib.sha256(str.encode(cookie)).hexdigest()

            user = User(username, token)
            db.session.add(user)
            db.session.commit()
            
            utc_time = None
            date = utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

            return {"token": token}, {'Set-Cookie': f'friday-login-token={token};Expires={date}'}
        else:
            abort(401, message=f"Password incorrect for {username}")

    def post(self, school):
        self.get(school)


