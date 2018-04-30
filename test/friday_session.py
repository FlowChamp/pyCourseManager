import requests
import getpass

class FridaySession:
    def __init__(self, username=None, password=None, url=None, email=None):
        self.URL = "http://127.0.0.1:4500/api/cpslo" if url is None else url
        self.EMAIL = "james.r.heald@gmail.com" if email is None else email 

        if username is None:
            username = input("Username: ") 

        if password is None:
            password = getpass.getpass()

        self.session = requests.Session()
        self.session.auth = (username, password)

        self.username = username 
        
        self.responses = {}
        self.last_response = None
        self.signup_token = None

        self.config = {}

        self.charts = []

    def get_wrapper(self, endpoint):
        resp = self.session.get(f"{self.URL}/{endpoint}")
        self.responses[endpoint] = resp
        self.last_response = resp

        return resp

    def post_wrapper(self, endpoint, json):
        resp = self.session.post(f"{self.URL}/{endpoint}", json=json)
        self.responses[endpoint] = resp
        self.last_response = resp

        return resp

    def get_pin(self):
        resp = self.post_wrapper("getpin", {"email": self.EMAIL})

        self.signup_token = resp.json().get("token")
        if self.signup_token is None:
            print("[ERROR] Something went wrong...")
            print(f"[{resp.status_code}]: {resp.json()}") 

    def sign_up(self, pin=None):
        if pin is None:
            pin = input("Please provide a PIN: ") 
        
        resp = self.post_wrapper("signup", {"token": self.signup_token, "pin": pin, "remember": 1})

        if resp.status_code != 200:
            print("[ERROR] Something went wrong...")
            print(f"[{resp.status_code}]: {resp.json()}")
        else:
            print("Signup complete, here are the cookies: ")
            print(resp.cookies)

        self.config = resp.json()

    def authorize(self): 
        resp = self.post_wrapper("authorize", {"remember": 1})

        if resp.status_code != 200:
            print("[ERROR] Something went wrong...")
            print(f"[{resp.status_code}]: {resp.json()}")
            return

        print(f"Authentication successful for user {self.username}")
        self.config = resp.json()
        

    def test_auth(self):
        resp = self.get_wrapper(f"users/{self.username}")

        if resp.status_code != 200:
            print("[ERROR] Authentication unsuccessful")
            print(f"[{resp.status_code}]: {resp.json()}")
            print(resp.cookies)
            exit(1)
        else:
            print(f"User {self.username} successfully authenticated")

    def post_config(self):
        resp = self.post_wrapper(f"users/{self.username}/config", self.config)

        if resp.status_code != 201:
            print("[ERROR] Something went wrong...")
            print(f"[{resp.status_code}]: {resp.json()}")
        else:
            print(f"Successfully updated config for user {self.username}")
    
    def load_charts(self):
        resp = self.get_wrapper("stock_charts/15-17")
        self.charts = resp.json()['charts']

    def import_chart(self, chart=None):
        resp = self.post_wrapper(f"users/{self.username}/import", {"target": "Computer_Science", "destination": "Unknown", "year": "15-17"})

        if resp.status_code != 201:
            print("[ERROR] Something went wrong...")
            print(f"[{resp.status_code}]: {resp.json()}")
            return

        self.config = resp.json()

