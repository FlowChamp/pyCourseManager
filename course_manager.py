"""
Notes:
    * for any request requiring the user to be logged in, the corresponding function
        must have a 'user' and 'school' argument
"""

import json, os
from datetime import datetime

from flask import request
from flask_restful import Resource, abort

# from login_manager import User, requires_login
from login import User, requires_login
from bson import ObjectId

def dereference_chart_ids(client, school, chart):
    """
    MongoClient string dict -> dict

    Convert the chart of block metadata into a split chart, that contains courses
    of both course data and block metadata
    """
    new_chart = {}
    for block in chart:
        db_name = f"{school}-catalog"
        bid_obj = block.pop('_id', None)
        bid = str(bid_obj)
        block['_id'] = bid
        new_chart[bid] = {}
        
        if 'catalog_id' in block:
            dept = block["department"]

            if isinstance(block['catalog_id'], list):
                courses = []
                cids = []
                ids = block.pop('catalog_id', None)
                for cid in ids:
                    course_data = client[db_name][dept].find_one(cid)
                    cid_str = str(course_data["_id"])
                    course_data["_id"] = cid_str 
                    courses.append(course_data)
                    cids.append(cid_str)
                block['catalog_id'] = cids 
                new_chart[bid]['course_data'] = courses
            else:
                cid_obj = block.pop('catalog_id', None)
                course_data = client[db_name][dept].find_one(cid_obj)
                cid = str(course_data["_id"])
                course_data["_id"] = cid
                block['catalog_id'] = cid
                new_chart[bid]['course_data'] = course_data

        new_chart[bid]['block_metadata'] = block

    return new_chart 

# /stock_charts
class ListStockYears(Resource):
    def __init__(self, client):
        self.client = client

    def get(self, school):
        years = []
        db_start = f"{school}-stockcharts"
        for db_name in self.client.database_names():
            if db_name.startswith(db_start):
                split = db_name.split('_')
                if len(split) == 2:
                    years.append(split[1])

        if not len(years):
            abort(404, message=f"There are no stock flowcharts for school {school}")

        return {'charts': years}

# /stock_charts/<year>
class ListStockCharts(Resource):
    def __init__(self, client):
        self.client = client

    def get(self, school, year):
        db_name = f"{school}-stockcharts_{year}"
        if db_name not in self.client.database_names():
            abort(404, message=f"School {school} does not contain any stock charts for the year {year}")

        charts = list(self.client[db_name].major_mapping.find())
        for x in charts:
            del x["_id"]

        return {'charts': charts}

# /stock_charts/<year>/<chart>
class GetStockChart(Resource):
    def __init__(self, client):
        self.client = client

    def get(self, school, year, major):
        db_name = f"{school}-stockcharts_{year}"
        chart = self.client[db_name][major].find()
        if chart:
            return dereference_chart_ids(self.client, school, chart) 
        else:
            abort(404, message=f"Either year is invalid or major does not exist") 

# /api/<school>/users/<user>
class TestUserAuth(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user):
        return {"message": f"User {user} at school {school} is " +
                "successfully authenticated for this endpoint"}, 200

# /api/<school>/users/<user>/config
class UserConfig(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user):
        userdb = f"{school}-{user}" 
        config = self.client[userdb].config.find_one()
        del config['_id']
        return config

    @requires_login
    def post(self, school, user):
        new_config = request.get_json()
        if not new_config:
            abort(400, message="No config data received")

        userdb = f"{school}-{user}"

        conf_id = self.client[userdb].config.find_one()['_id']
        self.client[userdb].config.update_one({'_id': conf_id}, {"$set": new_config}, upsert=True)
        return {"message": "Config successfully updated"}, 201

# /api/<school>/users/<user>/charts
class ListUserCharts(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user):
        # check_config_init(self.client, school, user)

        userdb = f"{school}-{user}" 
        # There's only one document in the config collection
        charts = self.client[userdb].config.find_one()['charts']

        if len(charts) == 0: 
            abort(404, message=f"User {user} has no charts")
        
        return list(charts)

# /api/<school>/users/<user>/import
class NewChartResource(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def post(self, school, user):
        userdb = f"{school}-{user}" 
        config = self.client[userdb].config.find_one()

        command = request.get_json()
        if not ('target' in command and 'destination' in command and 'year' in command):
            abort(400, message=("Copy command malformed. Please send a request "
                'of the form {"target": "target_stock_chart", "destination": '
                '"destination_chart_name"}'))

        target, year, destination = [command['target'], command['year'], command['destination']]
        if destination in config['charts']:
            print(config['charts'])
            abort(409, message=(f"Chart {destination} already exists on this server. "
                "Please choose a different name."))

        user_collection = self.client[userdb][destination]

        stock_chart = list(self.client[f"{school}-stockcharts_{year}"][target].find())
        if not len(stock_chart):
            abort(404, message=("Target chart not found. "
                "Either year is invalid or major does not exist")) 
        
        new_chart = []
        for block in stock_chart:
            del block["_id"]
            new_chart.append(block)

        config['charts'][destination] = target
        config['active_chart'] = destination
        self.client[userdb].config.update_one({"_id": config["_id"]}, {"$set": config}, upsert=False)

        user_collection.insert_many(new_chart)
        del config['_id']
        return config, 201

# /api/<school>/users/<user>/charts/<chart>
class ChartResource(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user, chart):
        userdb = f"{school}-{user}" 
        chart = self.client[userdb][chart].find()
        if chart is None:
            abort(404, message=f"Chart {chart} does not exist") 

        return dereference_chart_ids(self.client, school, chart) 

    @requires_login
    def post(self, school, user, chart):
        """This endpoint allows users to post new courses to their charts.
        It will return the ID of the newly added course
        """
        userdb = f"{school}-{user}" 

        block_metadata = request.get_json()
        if block_metadata is None:
            abort(400, message="Please send a new course to post to this chart") 

        user_chart = self.client[userdb][chart]
        cid = str(user_chart.insert_one(block_metadata).inserted_id)

        return {"_id": cid}, 201

    @requires_login
    def delete(self, school, user, chart):
        userdb = f"{school}-{user}" 

        user_chart = self.client[userdb][chart]
        if user_chart is None:
            abort(404, message=f"Chart {chart} was not found for this user")

        config = self.client[userdb].config.find_one()
        del config['charts'][chart]
        if config['active_chart'] == chart:
            config['active_chart'] = ''

        self.client[userdb].config.update_one({"_id": config["_id"]}, {"$set": config}, upsert=False)

        user_chart.drop()
        config["_id"] = str(config["_id"])

        return config, 200

# /api/<school>/users/<user>/charts/<chart>/<cid>
class CourseResource(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user, chart, c_id):
        userdb = f"{school}-{user}" 
        course = self.client[userdb][chart].find_one({"_id": ObjectId(c_id)})
        if course is None:
            abort(404, message=f"No course with id {c_id} found for chart {chart}")
        
        course['_id'] = str(course['_id'])
        return course 

    @requires_login
    def put(self, school, user, chart, c_id):
        new_course = request.get_json()
        if new_course is None:
            abort(400, message=f"Please send a new course to update the course at {c_id}")

        userdb = f"{school}-{user}" 
        course = self.client[userdb][chart].find_one({"_id": ObjectId(c_id)})
        if course is None:
            abort(404, message=f"No course with id {c_id} found for chart {chart}")

        # Fix new course info
        del new_course['_id']
        cat_id = new_course['catalog_id']

        if isinstance(cat_id, list):
            new_course['catalog_id'] = [ObjectId(x) for x in cat_id]
        else:
            new_course['catalog_id'] = ObjectId(cat_id)

        self.client[userdb][chart].update_one({"_id": ObjectId(c_id)}, {"$set": new_course}, upsert=False)

        return 201 

    @requires_login
    def delete(self, school, user, chart, c_id):
        userdb = f"{school}-{user}" 
        course = self.client[userdb][chart].find_one({"_id": ObjectId(c_id)})
        if course is None:
            abort(404, message=f"No course with id {c_id} found for chart {chart}")
        
        self.client[userdb][chart].delete_one({"_id": ObjectId(c_id)})

        return 201 
