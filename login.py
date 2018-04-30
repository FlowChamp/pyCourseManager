import os, hashlib, json 
import requests
from flask import request
from flask_restful import Resource, abort
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

import smtplib
from email.mime.text import MIMEText
import requests

import secret
import random

db = SQLAlchemy()

USER_TOKENS = {}

class UserPin:
    def __init__(self, email, pin):
        self.email = email
        self.pin = int(pin)
        self.expiry = datetime.now() + timedelta(minutes=20)

    def is_valid(self, p):
        correct_pin = (self.pin == int(p))
        expired = (datetime.now() > self.expiry)
        
        if expired:
            return (False, "PIN has expired")
        elif not correct_pin:
            return (False, "Incorrect PIN")
        else:
            return (True, "Success")

    def __str__(self):
        return f"{self.email}: {self.pin}"

def email_pin(pin, user):
    email_user = secret.email_user
    email_password = secret.email_password

    email = f"Please use the following PIN for flowchamp.org: {pin}"

    msg = MIMEText(email)
    msg['Subject'] = "Authentication for flowchamp.org" 
    msg['From'] = email_user
    msg['To'] = user 

    server = smtplib.SMTP('40.97.162.114', 25)
    server.ehlo()
    server.starttls()
    server.login(email_user, email_password)
    server.sendmail(email_user, [user], msg.as_string())
    server.quit()

def check_config_init(client, username, school):
    full_username = f"{school}-{username}"
    if full_username not in client.database_names():
        if client[full_username].config.count() == 1:
            return

        config = {
            "username": username,
            "start_year": 0,
            "active_chart": "",
            "charts": {}
        }
        client[full_username].config.insert_one(config)

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
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    token = db.Column(db.String(80))
    token_expiration = db.Column(db.DateTime())
    is_authorized = db.Column(db.Boolean())

    def __init__(self, username, email, token, remember=None):
        self.username = username
        self.email = email
        self.set_token(token, remember)

    def set_token(self, token, remember=None):
        self.token = generate_password_hash(token)
        if remember:
            self.token_expiration = datetime.now() + timedelta(days=365)
        else:
            self.token_expiration = datetime.now() + timedelta(minutes=30)
    

    def check_token(self, tk):
        return check_password_hash(self.token, tk) 

    def set_password(self, pw):
        self.password = generate_password_hash(self.username + pw)

    def check_password(self, pw):
        return check_password_hash(self.password, self.username + pw)
    
    def is_expired(self):
        return datetime.now() > self.token_expiration

    def __str__(self):
        return f"{self.username}: {self.token}"
    def __repr__(self):
        return '<User %r>' % self.username

class PinResource(Resource):
    def __init__(self, client):
        self.client = client
    
    def post(self, school):
        args = request.get_json()
        user_email = args.get('email')
        if not user_email:
            abort(400, message="Please provide an email to send the user a pin")
        

        pin = random.randint(99999, 999999)
        email_pin(pin, user_email)

        token = hashlib.sha256(str.encode(user_email + str(datetime.now()) + str(pin))).hexdigest()

        USER_TOKENS[token] = UserPin(user_email, pin)

        return {"token": token}
    
class SignUpResource(Resource):
    def __init__(self, client):
        self.client = client
    
    def post(self, school):
        args = request.get_json()
        username = request.authorization.username
        password = request.authorization.password

        pin = args.get('pin')
        # Token to check PIN validity against
        ptoken = args.get('token')

        if not pin:
            abort(403, message=f"Please provide a PIN")

        user_info = USER_TOKENS.get(ptoken)
        if not user_info:
            abort(404, message=f"Token {ptoken} is not a valid user token")

        pin_is_valid, msg = user_info.is_valid(pin) 
        if not pin_is_valid:
            abort(403, message=msg)

        # Set a token to be used to authorize against resources
        token = hashlib.sha256(str.encode(user_info.email + str(datetime.now()))).hexdigest()
        full_username = f"{school}-{username}"

        tmp_user = User.query.filter_by(username=full_username).first()
        if tmp_user is not None:
            abort(400, message=f"User {full_username} already exists, please sign in instead")

        rem = True if args.get("remember") else False
        user = User(full_username, user_info.email, token, remember=rem)
        user.set_password(password)
        user.is_authorized = True
        db.session.add(user)
        db.session.commit()

        del USER_TOKENS[ptoken]

        check_config_init(self.client, username, school) 
        config = self.client[full_username].config.find_one()
        del config['_id']
        
        utc_time = datetime.utcnow() 
        utc_time += timedelta(days=365) if rem else timedelta(minutes=30)
        date = utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

        return config, {'Set-Cookie': f'friday-login-token={token};Expires={date}'}

    def put(self, school):
        pass

class AuthorizeResource(Resource):
    def __init__(self, client):
        self.client = client

    """Send a GET request to the API to authenticate the user. If the user 
    authentication succeeds, give the client a grant token"""
    def get(self, school):
        args = request.get_json()
        username = request.authorization.username
        password = request.authorization.password

        token = hashlib.sha256(str.encode(username + str(datetime.now()))).hexdigest()

        email_name = None
        email_pos = username.find('@')
        if email_pos == -1:
            email_name = username
        else:
            email_name = username[:username.find('@')]

        full_username = f"{school}-{email_name}"
        if args:
            rem = True if args.get("remember") else False
        else:
            rem = False

        tmp_user = User.query.filter_by(username=full_username).first()
        if tmp_user is not None:
            if not tmp_user.check_password(password):
                abort(401, message=f"Incorrect password for user {username}")

            tmp_user.set_token(token, remember=rem)
        else:
            abort(409, message=f"User {username} does not exist")

        db.session.commit()
        
        check_config_init(self.client, username, school) 
        config = self.client[full_username].config.find_one()
        del config['_id']
        
        utc_time = datetime.utcnow() 
        utc_time += timedelta(days=365) if rem else timedelta(minutes=30)
        date = utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

        return config, {'Set-Cookie': f'friday-login-token={token};Expires={date}'}

    def post(self, school):
        return self.get(school)

class LogoutResource(Resource):
    @requires_login
    def post(self, school, user):
        # requires_login ensures that there will be a user before we get here
        username = f"{school}-{user}"

        user = User.query.filter_by(username=username).first()
        user.set_token('')
        user.is_authorized = False

        db.session.commit()

        return {"message": f"User {user} successfully logged out"}

