import os, hashlib, json 
import requests
from flask import request
from flask_restful import Resource, abort

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import lxml.html

class LoginResource(Resource):
    """Send a POST request to the API to authenticate the user. If the user 
    authentication succeeds, give the client a grant token"""
    def get(self, school):
        print(request.headers)
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
            """Plan: 
                1) Get cookie
                2) Get expiration
                3) Hash cookie, to store in database 
                4) Store username, hashed cookie, and expiration in database
                5) Return cookie 
            """
            cookie = resp.cookies['org.jasig.portal.PORTLET_COOKIE']
            expiry = resp.cookies['sessionExpiry']
            token = generate_password_hash(cookie)

            return {"token": cookie}, {'Set-Cookie': f'token={cookie}'}
        else:
            abort(401, message=f"Password incorrect for {username}")

    def post(self, school):
        self.get(school)


