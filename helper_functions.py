import requests, json 

url = "http://127.0.0.1:4500"

def make_headers(func):
    def headers_from_input(*args):
        headers=None
        json_headers = {'content-type': 'application/json'}
        auth_headers={'x-api-key': ''}

        use_json = False
        use_key = True
        for x in args:
            if isinstance(x, dict):
                use_json = True
            elif len(x) == 40:
                use_key = True
                auth_headers['x-api-key'] = x

        if use_json and use_key:
            headers = {**json_headers, **auth_headers}
        elif use_json:
            headers = json_headers
        elif use_key:
            headers = auth_headers

        return func(*args, headers)
    return headers_from_input

def new_user(user, pw):
    return requests.post(f"{url}/useradd", auth=requests.auth.HTTPBasicAuth(user,pw))

def log_in(user, pw):
    return requests.get(f"{url}/authorize", auth=requests.auth.HTTPBasicAuth(user,pw))

@make_headers
def log_out(key, headers=None):
    return requests.post(f"{url}/logout", headers=headers)

def delete_user(user, pw):
    return requests.post(f"{url}/delete_user", auth=requests.auth.HTTPBasicAuth(user,pw))


def list_stock():
    return requests.get(f"{url}/stock_charts/2015-17")

def get_stock(chart):
    return requests.get(f"{url}/stock_charts/2015-17/{chart}")

@make_headers
def get_charts(user, key, headers=None):
    return requests.get(f"{url}/{user}/charts", headers=headers)

@make_headers
def get_chart(user, chart, key, headers=None):
    return requests.get(f"{url}/{user}/charts/{chart}", headers=headers).json()

@make_headers
def post_chart(user, chart, chart_dict, key, headers=None):
    return requests.post(f"{url}/{user}/charts/{chart}", data=json.dumps(chart_dict), headers=headers).json()

@make_headers
def delete_chart(user, chart, headers=None):
    return requests.delete(f"{url}/{user}/charts/{chart}", headers=headers)

@make_headers
def put_chart(user, chart, course, key, headers=None):
    return requests.put(f"{url}/{user}/charts/{chart}", data=json.dumps(course), headers=headers).json()

@make_headers
def get_course(user, chart, c_id, key, headers=None):
    return requests.get(f"{url}/{user}/charts/{chart}/{c_id}", headers=headers).json()

@make_headers
def put_course(user, chart, c_id, course, key, headers=None ):
    return requests.put(f"{url}/{user}/charts/{chart}/{c_id}", data=json.dumps(course), headers=headers).json()

@make_headers
def delete_course(user, chart, c_id, key, headers=None):
    return requests.delete(f"{url}/{user}/charts/{chart}/{c_id}", headers=headers).json()

    

