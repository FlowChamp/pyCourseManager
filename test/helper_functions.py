import requests
import getpass

URL = "http://127.0.0.1:4500/api/cpslo"
EMAIL = "james.r.heald@gmail.com"

def make_session(username=None, password=None):
    if username is None:
        username = input("Username: ") 

    if password is None:
        password = getpass.getpass()

    sess = requests.Session()
    sess.auth = (username, password)
    return (sess, username)

def get_pin(session, email):
    resp = session.post(f"{URL}/getpin", json={"email": email})

    token = resp.json().get("token")
    if token is None:
        print("[ERROR] Something went wrong...")
        print(f"[{resp.status_code}]: {resp.json()}")
        exit(1)

    return token 

def sign_up(session, token, pin):
    resp = session.post(f"{URL}/signup", json={"token": token, "pin": pin, "remember": 1})

    if resp.status_code != 200:
        print("[ERROR] Something went wrong...")
        print(f"[{resp.status_code}]: {resp.json()}")
        exit(1)
    else:
        print("Signup complete, here are the cookies: ")
        print(resp.cookies)

def authorize(session, username): 
    resp = session.get(f"{URL}/authorize", json={"remember": 1})
    if resp.status_code != 200:
        print("[ERROR] Something went wrong...")
        print(f"[{resp.status_code}]: {resp.json()}")
        exit(1)
    else:
        print(f"Authentication successful for user {username}")

def test_auth(session, username):
    resp = session.get(f"{URL}/users/{username}")
    if resp.status_code != 200:
        print("[ERROR] Authentication unsuccessful")
        print(f"[{resp.status_code}]: {resp.json()}")
        print(resp.cookies)
        exit(1)
    else:
        print(f"User {username} successfully authenticated")

