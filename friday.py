import json, os
from flask import Flask, request
from flask_restful import reqparse, Resource, Api, abort
from datetime import datetime 

app = Flask(__name__)
api = Api(app)

courses = {}
last_course_ids = {}
# ge_map = {}        

# This will be the responsibility of the client to implement
# user = {
    # 'year': 1
    # }

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

# parser = reqparse.RequestParser()
# parser.add_argument('course', type=str)
# parser.add_argument('chart', type=str)

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
        courses[user] = {}

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

        args = parser.parse_args()
        # new_chart_raw = args['chart']
        new_chart = json.loads(request.data)
        
        

        # load_courses(user, chart, {'temp': new_chart}) 

        # with open(path, 'w') as flowfile:
            # outp_data = {
                    # 'temp' : courses[user][chart]
                    # }
            # flowfile.write(json.dumps(outp_data, indent=4))

        # return new_chart, 201

    @check_if_loaded 
    def put(self, user, chart):
        # print("Putting!")
        global last_course_ids
        global courses 
        
        args = parser.parse_args()
        # new_course_raw = args['course']
        new_course = json.loads(request.data)
        # print(new_course)
        
        # c_id = last_course_ids[user][chart] + 1
        # last_course_ids[user][chart] += 1
        
        # print(type(course[user][chart]))
        # courses[user][chart][c_id] = new_course  

        # return { c_id: new_course }, 201
    
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
        course = dict(request.form)
        print(course)
        return courses[user][chart][c_id]

    @check_if_loaded
    def delete(self, user, chart, c_id):
        return courses[user][chart][c_id]

api.add_resource(ListStockCharts, '/stock_charts')
api.add_resource(ListUserCharts,  '/<string:user>/charts')
api.add_resource(GetStockChart,   '/stock_charts/<string:major>')
api.add_resource(ChartResource,   '/<string:user>/charts/<string:chart>')
api.add_resource(CourseResource,  '/<string:user>/charts/<string:chart>/<int:c_id>')

if __name__ == '__main__':
    app.run(debug=True)

