import json, os
from flask import Flask, request
from flask_restful import reqparse, Resource, Api, abort
from datetime import datetime 

app = Flask(__name__)
api = Api(app)

courses = {}
last_course_ids = {}

today = datetime.today()

fall = datetime(today.year, 9, 15)
winter = datetime(today.year, 1, 1)
spring = datetime(today.year, 3, 31)
summer = datetime(today.year, 6, 15)

if fall <= today <= datetime(today.year, 12, 31):
    quarter = 0
elif winter <= today < spring:
    quarter = 1
elif spring <= today < summer:
    quarter = 2
else:
    quarter = 3

# This should be read from a config file
course_root = "/srv/pyflowchart/"

def check_if_loaded(func):
    def func_wrapper(self, **kwargs):
        user  = kwargs['user']
        chart = kwargs['chart']

        if user not in courses:
            load_user_chart(user, chart)
        elif chart not in courses[user]:
            load_user_chart(user, chart)
        
        outp = func(self, **kwargs)

        save_courses(user, chart)
        return outp
    
    return func_wrapper 

def load_course_file(path):
    if not os.path.isfile(path):
        abort(404, message=f"File {path} does not exist")
    
    with open(path, 'r') as jsonfile:
        try:
            file_courses = json.loads(jsonfile.read())
        except ValueError: 
            abort(500, message=(f"JSON file {path} invalid or corrupt. "
                "Please contact your server administrator"))

    return file_courses 

def load_courses(user, chart, course_dict):
    global courses
    global last_course_ids 
    
    if user not in courses:
        print(f"Loading user {user}")
        courses[user] = {}

    print(f"Loading {user}/{chart}")
    courses[user][chart] = {}
    
    if user not in last_course_ids:
        last_course_ids[user] = {}
    
    course_ids = []
    
    user_courses = {} 
    for course_id, course in next(iter(course_dict.values())).items():
        course_id = int(course_id)
        user_courses[course_id] = course
        course_ids.append(course_id)

    last_course_id = max(course_ids)

    courses[user][chart] = user_courses
    last_course_ids[user][chart] = last_course_id 
    return user_courses

def load_user_chart(user,chart):
    path = course_root + "users/" + user + "/charts/" + chart + ".json" 
    file_courses = load_course_file(path)
    return load_courses(user, chart, file_courses)

def save_courses(user, chart):
    """Save all courses to the given filename."""
    path = course_root + "users/" + user + "/charts/" + chart + ".json" 

    with open(path, 'w') as flowfile:
        outp_data = {
                'temp' : courses[user][chart]
                }
        flowfile.write(json.dumps(outp_data, indent=4))

# /
class UsageResource(Resource):
    def get(self):
        return {"Usage": {
"/stock_charts": {
    "GET": {
        "Returns": "A listing of all available stock charts"
        }
    },

"/<string:user>/charts": {
    "GET": { 
        "Returns": "A listing of all charts available for the user"
        }
    },

"/stock_charts/<string:major>":
    "GET": { 
        "Returns": "The stock flowchart for <major>"
        }
    },

"/<string:user>/charts/<string:chart>": {
    "GET": { 
        "Returns": "The user's flowchart"
        },
    "POST": {
        "Description": "Create a new flowchart of name <chart>",
        "Returns": "The new flowchart",
        "Note": "Chart cannot exist; if it does, please delete it first"
        },
    "PUT": { 
        "Description": "Append a course to the flowchart",
        "Returns": "The course data wrapped with the course ID assigned"
        },
    "DELETE": {
        "Descripition": "Deletes the flowchart from the server"
        }
    },

"/<string:user>/charts/<string:chart>/<int:id>": {
    "GET": {
        "Returns": "The course of id <id>"
        },
    "PUT": {
        "Description" :"Updates the course at given id",
        "Returns": "The new course at given id"
        },
    "DELETE": { 
        "Description": "Deletes the course"
        }
    }
}
}

# /stock_charts
class ListStockCharts(Resource):
    def get(self):
        return {'charts': os.listdir(course_root + "stock_charts")}

# /<user>/charts
class ListUserCharts(Resource):
    def get(self, user):
        return {'charts': os.listdir(course_root + "users/" + user + "/charts/")}
    
# /stock_charts/<chart>
class GetStockChart(Resource):
    def get(self, major):
        path = course_root + "stock_charts/" + major + ".json" 
        return load_course_file(path)

# /<user>/charts/<chart>
class ChartResource(Resource):
    @check_if_loaded 
    def get(self, user, chart):
        return courses[user][chart]
    
    def post(self, user, chart):
        global courses
        course_ids = []

        path = course_root + "users/" + user + "/charts/" + chart + ".json" 
        if os.path.exists(path):
            abort(403, message=f"Will not overwrite {chart}. Please delete existing chart first")

        new_chart = json.loads(request.form)

        load_courses(user, chart, {'temp': new_chart}) 

        with open(path, 'w') as flowfile:
            outp_data = {
                    'temp' : courses[user][chart]
                    }
            flowfile.write(json.dumps(outp_data, indent=4))

        return new_chart, 201

    @check_if_loaded 
    def put(self, user, chart):
        global last_course_ids
        global courses 
        
        new_course = dict(request.form)
        
        c_id = last_course_ids[user][chart] + 1
        last_course_ids[user][chart] += 1
        
        courses[user][chart][c_id] = new_course  

        return { c_id: new_course }, 201
    
    def delete(self, user, chart):
        global courses
        path = course_root + "users/" + user + "/charts/" + chart + ".json"
        if user in courses and chart in courses[user]:
            del courses[user][chart] 
        os.remove(path)
        return 200
        

# /<user>/charts/<chart>/<id>
class CourseResource(Resource):
    @check_if_loaded
    def get(self, user, chart, c_id):
        return courses[user][chart][c_id]
    
    @check_if_loaded 
    def put(self, user, chart, c_id):
        global courses 

        course = dict(request.form)
        courses[user][chart][c_id] = course

        return courses[user][chart][c_id]

    @check_if_loaded
    def delete(self, user, chart, c_id):
        global courses
        del courses[user][chart][c_id]
        return 200 

api.add_resource(UsageResource,   '/')
api.add_resource(ListStockCharts, '/stock_charts')
api.add_resource(ListUserCharts,  '/<string:user>/charts')
api.add_resource(GetStockChart,   '/stock_charts/<string:major>')
api.add_resource(ChartResource,   '/<string:user>/charts/<string:chart>')
api.add_resource(CourseResource,  '/<string:user>/charts/<string:chart>/<int:c_id>')

if __name__ == '__main__':
    app.run(debug=True)

