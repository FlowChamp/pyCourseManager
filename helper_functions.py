import requests, json 

url = "http://ssh.marshhouse.tech:6500"
headers = {'content-type': 'application/json'}

def get_chart(chart):
    return requests.get(f"{url}/jrheald/charts/{chart}").json()

def post_chart(chart, chart_dict):
    return requests.post(f"{url}/jrheald/charts/{chart}", data=json.dumps(chart_dict), headers=headers).json()

def delete_chart(chart):
    return requests.delete(f"{url}/jrheald/charts/{chart}")

def put_chart(chart, course):
    return requests.put(f"{url}/jrheald/charts/{chart}", data=json.dumps(course), headers=headers).json()

def get_course(chart, c_id):
    return requests.get(f"{url}/jrheald/charts/{chart}/{c_id}").json()

def put_course(chart, c_id, course):
    return requests.put(f"{url}/jrheald/charts/{chart}/{c_id}", data=json.dumps(course), headers=headers).json()

def delete_course(chart, c_id):
    return requests.delete(f"{url}/jrheald/charts/{chart}/{c_id}")

    

