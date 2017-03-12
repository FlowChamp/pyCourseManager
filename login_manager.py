import os, sqlalchemy, hashlib

from flask import request
from flask_login import *
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, abort

from functools import wraps

db = SQLAlchemy()
login_manager = LoginManager()

def requires_login(func):
    @wraps(func)
    def try_token(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            global current_user 
            current_user = user 
            if user.username in args:
                print("You bet!")
                return func(*args, **kwargs)
        else:
            return login_required(func)(*args, **kwargs)
    return try_token      

@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('x-api-key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user
    
    if request.authorization:
        username = request.authorization.username  
        user = User.query.filter_by(username=username).first() 
        if user:
            return user

    return None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    api_key = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.api_key = ''

    def check_password(self, pw):
        return pw == self.password

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True 

    @property
    def is_anonymous(self):
        return False 
    
    def get_id(self):
        return self.username
    
    def __str__(self):
        return f"{self.username}: {self.api_key}"
    def __repr__(self):
        return '<User %r>' % self.username

class LoginManager():
    # /useradd 
    class NewUserResource(Resource):
        def post(self):
            try:
                print(request)
                data = request.get_json()
                username = data['username']
                password = data['password']

                if not password: 
                    abort(401, message=f"Please provide password for {username} in the 'x-api-key' header")
                
                db.session.add(User(username, password))
                db.session.commit()
                return {"message": "User created successfully"}
            except sqlalchemy.exc.IntegrityError:
                abort(409, message=f"User {username} already exists")

    # /authorize 
    class LoginResource(Resource):
        """Send a POST request to the API to authenticate the user. If the user 
        authentication succeeds, give the client a grant token"""
        def post(self):
            username = request.authorization.username
            password = request.authorization.password
            user = User.query.filter_by(username=username).first() 

            if user:
                if user.check_password(password):
                    # Let's create a token
                    ip = request.remote_addr
                    client_id = f"{username}@{ip}"
                    token = hashlib.sha1(os.urandom(128)).hexdigest() 
                    
                    # Add the token to the user
                    user.api_key = token
                    db.session.commit()

                    login_user(user)
                    print(user)
                    return {"x-api-key": token}
                else:
                    abort(401, message=f"Password incorrect for {username}")
            else:
                abort(404, message=f"User {username} does not exist")

    # /logout
    class LogoutResource(Resource):
        def post(self):
            api_key = request.headers.get('x-api-key')
            print(request.headers)
            user = User.query.filter_by(api_key=api_key).first()
            print(user)
            if user:
                global current_user
                current_user = user
                logout_user()
                return {"message": "User logged out"}
            else:
                abort(410, message="No user associated with the given api key")
