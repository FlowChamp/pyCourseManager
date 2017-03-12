import os, sqlalchemy, hashlib, json 

from flask import request
from flask_login import *
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, abort

from functools import wraps
from datetime import datetime, timedelta 

db = SQLAlchemy()
login_manager = LoginManager()

### THIS NEEDS TO BE READ FROM A FILE ###
course_root = "/srv/pyflowchart"

def requires_login(func):
    @wraps(func)
    def try_token(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            global current_user 
            current_user = user 

            if user.username in kwargs.values():
                if user.is_expired():
                    abort(403, message="Api key expired, please reauthenticate")
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
    api_key_expiration = db.Column(db.DateTime())

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

    def set_api_key(self, key):
        self.api_key = key 
        self.api_key_expiration = datetime.now() + timedelta(minutes=30)

    def is_expired(self):
        return datetime.now() > self.api_key_expiration

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
                username = request.authorization.username
                password = request.authorization.password

                if not username or not password: 
                    abort(401, message=f"Please provide credentials using HTTP Basic Auth ")
                
                db.session.add(User(username, password))
                db.session.commit()
                
                # Make sure user has a chart dir
                user_dir = f"{course_root}/users/{username}"
                if not os.path.isdir(user_dir):
                    os.makedirs(user_dir+"/charts")

                if not os.path.exists(user_dir+"/config"):
                    with open(user_dir+"/config", 'a') as conf:
                        config = {
                                'userInfo' : {'year': 1,
                                              'display_years': 4},
                                'GEs'      : {}
                                }
                        conf.write(json.dumps(config, indent=4))


                return {"message": "User created successfully"}

            except sqlalchemy.exc.IntegrityError:
                abort(409, message=f"User {username} already exists")

    # /authorize 
    class LoginResource(Resource):
        """Send a POST request to the API to authenticate the user. If the user 
        authentication succeeds, give the client a grant token"""
        def get(self):
            username = request.authorization.username
            password = request.authorization.password
            user = User.query.filter_by(username=username).first() 

            if user:
                if user.check_password(password):
                    token = hashlib.sha1(os.urandom(128)).hexdigest() 
                    user.set_api_key(token)
                    db.session.commit()

                    login_user(user)
                    return {"x-api-key": token}
                else:
                    abort(401, message=f"Password incorrect for {username}")
            else:
                abort(404, message=f"User {username} does not exist")
        
        def post(self):
            get(self)

    # /logout
    class LogoutResource(Resource):
        def post(self):
            api_key = request.headers.get('x-api-key')
            if len(api_key) != 40:
                abort(401, message="Api key must be 40 characters in length")

            user = User.query.filter_by(api_key=api_key).first()
            if user:
                global current_user
                current_user = user
                logout_user()
                
                # Destroy the session key
                user.api_key = ''
                db.session.commit()

                return {"message": "User logged out"}
            else:
                abort(401, message="No user associated with the given api key")

    # /delete_account 
    class DeleteUserResource(Resource): 
        def post(self):
            username = request.authorization.username
            password = request.authorization.password

            if not username or not password: 
                abort(401, message="Please provide credentials using HTTP Basic Auth ")

            user = User.query.filter_by(username=username).first()
            if user is not None:
                db.session.delete(user)
                db.session.commit()
            else:
                abort(404, message=f"User {username} does not exist")
