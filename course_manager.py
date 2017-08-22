import json, os
from datetime import datetime

from flask import request
from flask_restful import Resource, abort

from login_manager import User, requires_login

class CourseManager():
    course_root = "/srv/pyflowchart/"
    courses = {}
    last_course_ids = {}

    def __init__(self, db):
        today = datetime.today()

        fall = datetime(today.year, 9, 15)
        winter = datetime(today.year, 1, 1)
        spring = datetime(today.year, 3, 31)
        summer = datetime(today.year, 6, 15)

        if fall <= today <= datetime(today.year, 12, 31):
            self.quarter = 0
        elif winter <= today < spring:
            self.quarter = 1
        elif spring <= today < summer:
            self.quarter = 2
        else:
            self.quarter = 3

        self.catalog_db = db.catalog

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

    # /stock_charts
    class ListStockYears(Resource):
        def __init__(self, client):
            self.client = client

        def get(self, school):
            return {'charts': self.client[school].stock_charts.distinct("year")}

    # /stock_charts/<year>
    class ListStockCharts(Resource):
        def __init__(self, client):
            self.client = client

        def get(self, school, year):
            return {'charts': 
                    self.client[school].stock_charts.find({"year": year}).distinct("major")}

    # /stock_charts/<year>/<chart>
    class GetStockChart(Resource):
        def __init__(self, client):
            self.client = client

        def get(self, school, year, major):
            chart = self.client[school].stock_charts.find({"year": year, "major": major})
            if chart:
                new_chart = {}
                for block in chart:
                    bid_obj = block.pop('_id', None)
                    bid = str(bid_obj)
                    new_chart[bid] = {}

                    if 'catalog_id' in block:
                        if isinstance(block['catalog_id'], list):
                            courses = []
                            ids = block.pop('catalog_id', None)
                            for cid in ids:
                                course_data = self.client[school].catalog.find_one(
                                        {"_id": cid})
                                course_data["_id"] = str(course_data["_id"])
                                courses.append(course_data)
                            new_chart[bid]['course_data'] = courses
                        else:
                            cid = block.pop('catalog_id', None)
                            course_data = self.client[school].catalog.find_one(
                                    {"_id": cid})
                            course_data["_id"] = str(course_data["_id"])
                            new_chart[bid]['course_data'] = course_data
                            

                    new_chart[bid]['block_metadata'] = block

                return new_chart 
            else:
                abort(404, message=f"Either year is invalid or major does not exist") 

    # /<user>/charts
    class ListUserCharts(Resource):
        @requires_login
        def get(self, user):
            return {'charts': [x[:x.find(".json")] 
                for x in os.listdir(
                    CourseManager.course_root + "users/" + user + "/charts/")]}
        
    # /<user>/charts/<chart>
    class ChartResource(Resource):
        @requires_login
        def get(self, user, chart):
            CourseManager.ensure_loaded(user, chart)
            return CourseManager.courses[user][chart]
        
        @requires_login
        def post(self, user, chart):
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
        
        @requires_login
        def put(self, user, chart):
            new_course = request.get_json()
            
            c_id = CourseManager.last_course_ids[user][chart] + 1
            CourseManager.last_course_ids[user][chart] += 1
            
            CourseManager.courses[user][chart][c_id] = new_course  
            CourseManager.save_courses(user, chart)

            return { c_id: new_course }, 201
        
        @requires_login
        def delete(self, user, chart):
            path = CourseManager.course_root + "users/" + user + "/charts/" + chart + ".json"
            if user in CourseManager.courses and chart in CourseManager.courses[user]:
                del CourseManager.courses[user][chart] 
            os.remove(path)
            return 200
            

# /<user>/charts/<chart>/<id>
    class CourseResource(Resource):
        @requires_login
        def get(self, user, chart, c_id):
            CourseManager.ensure_loaded(user, chart)
            return CourseManager.courses[user][chart][c_id]
        
        @requires_login
        def put(self, user, chart, c_id):
            CourseManager.ensure_loaded(user, chart)
            course = request.get_json()
            CourseManager.courses[user][chart][c_id] = course
            CourseManager.save_courses(user, chart)

            return CourseManager.courses[user][chart][c_id]
        
        @requires_login
        def delete(self, user, chart, c_id):
            CourseManager.ensure_loaded(user, chart)
            del CourseManager.courses[user][chart][c_id]
            CourseManager.save_courses(user, chart)
            return 200 
