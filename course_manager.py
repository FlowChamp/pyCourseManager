import json, os
from flask import request
from flask_restful import Resource, abort

class CourseManager():
    course_root = "/srv/pyflowchart/"
    courses = {}
    last_course_ids = {}

    def ensure_loaded(user, chart):
        if user not in CourseManager.courses:
            CourseManager.load_user_chart(user, chart)
        elif chart not in CourseManager.courses[user]:
            CourseManager.load_user_chart(user, chart)

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
        if user not in CourseManager.courses:
            print(f"Loading user {user}")
            CourseManager.courses[user] = {}

        print(f"Loading {user}/{chart}")
        CourseManager.courses[user][chart] = {}
        
        if user not in CourseManager.last_course_ids:
            CourseManager.last_course_ids[user] = {}
        
        course_ids = []
        
        user_courses = {} 
        for course_id, course in next(iter(course_dict.values())).items():
            course_id = int(course_id)
            user_courses[course_id] = course
            course_ids.append(course_id)

        last_course_id = max(course_ids)

        CourseManager.courses[user][chart] = user_courses
        CourseManager.last_course_ids[user][chart] = last_course_id 
        return user_courses

    def load_user_chart(user,chart):
        path = CourseManager.course_root + "users/" + user + "/charts/" + chart + ".json" 
        file_courses = CourseManager.load_course_file(path)
        return CourseManager.load_courses(user, chart, file_courses)

    def save_courses(user, chart):
        """Save all courses to the given filename."""
        path = CourseManager.course_root + "users/" + user + "/charts/" + chart + ".json" 

        with open(path, 'w') as flowfile:
            outp_data = {
                    'temp' : CourseManager.courses[user][chart]
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

    "/stock_charts/<string:major>": {
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
            "Accepts" : "Flowchart in JSON format. Must be sent with application/json content header",
            "Returns": "The new flowchart",
            "Note": "Chart cannot exist; if it does, please delete it first."
            },
        "PUT": { 
            "Description": "Append a course to the flowchart",
            "Accepts" : "Course in JSON format. Must be sent with application/json content header",
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
            "Accepts" : "Course in JSON format. Must be sent with application/json content header",
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
            print("Listing stock!")
            return {'charts': [x[:x.find(".json")] 
                for x in os.listdir(
                    CourseManager.course_root + "stock_charts")]}

# /<user>/charts
    class ListUserCharts(Resource):
        def get(self, user):
            return {'charts': [x[:x.find(".json")] 
                for x in os.listdir(
                    CourseManager.course_root + "users/" + user + "/charts/")]}
        
# /stock_charts/<chart>
    class GetStockChart(Resource):
        def get(self, major):
            path = CourseManager.course_root + "stock_charts/" + major + ".json" 
            return CourseManager.load_course_file(path)

# /<user>/charts/<chart>
    class ChartResource(Resource):
        def get(self, user, chart):
            CourseManager.ensure_loaded(user, chart)
            return CourseManager.courses[user][chart]
        
        def post(self, user, chart):
            print("You POSTed me!")
            course_ids = []

            path = CourseManager.course_root + "users/" + user + "/charts/" + chart + ".json" 
            if os.path.exists(path):
                abort(403, message=f"Will not overwrite {chart}. Please delete existing chart first")

            new_chart = request.get_json()

            CourseManager.load_courses(user, chart, {'temp': new_chart}) 

            with open(path, 'w') as flowfile:
                outp_data = {
                        'temp' : CourseManager.courses[user][chart]
                        }
                flowfile.write(json.dumps(outp_data, indent=4))

            return new_chart, 201
        
        def put(self, user, chart):
            print("You PUT me in my place!")
            new_course = request.get_json()
            
            c_id = CourseManager.last_course_ids[user][chart] + 1
            CourseManager.last_course_ids[user][chart] += 1
            
            CourseManager.courses[user][chart][c_id] = new_course  
            CourseManager.save_courses(user, chart)

            return { c_id: new_course }, 201
        
        def delete(self, user, chart):
            path = CourseManager.course_root + "users/" + user + "/charts/" + chart + ".json"
            if user in CourseManager.courses and chart in CourseManager.courses[user]:
                del CourseManager.courses[user][chart] 
            os.remove(path)
            return 200
            

# /<user>/charts/<chart>/<id>
    class CourseResource(Resource):
        def get(self, user, chart, c_id):
            CourseManager.ensure_loaded(user, chart)
            return CourseManager.courses[user][chart][c_id]
        
        def put(self, user, chart, c_id):
            print("You PUT me in my place!")
            CourseManager.ensure_loaded(user, chart)
            course = request.get_json()
            CourseManager.courses[user][chart][c_id] = course
            CourseManager.save_courses(user, chart)

            return CourseManager.courses[user][chart][c_id]

        def delete(self, user, chart, c_id):
            CourseManager.ensure_loaded(user, chart)
            del CourseManager.courses[user][chart][c_id]
            CourseManager.save_courses(user, chart)
            return 200 