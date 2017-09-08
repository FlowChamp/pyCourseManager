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

def dereference_chart_ids(client, school, chart):
    """
    MongoClient string dict -> dict

    Convert the chart of block metadata into a split chart, that contains courses
    of both course data and block metadata
    """
    new_chart = {}
    for block in chart:
        bid_obj = block.pop('_id', None)
        bid = str(bid_obj)
        block['_id'] = bid
        new_chart[bid] = {}

        if 'catalog_id' in block:
            if isinstance(block['catalog_id'], list):
                courses = []
                cids = []
                ids = block.pop('catalog_id', None)
                for cid in ids:
                    course_data = client[school].catalog.find_one(
                            {"_id": cid})
                    cid_str = str(course_data["_id"])
                    course_data["_id"] = cid_str 
                    courses.append(course_data)
                    cids.append(cid_str)
                block['catalog_id'] = cids 
                new_chart[bid]['course_data'] = courses
            else:
                cid_obj = block.pop('catalog_id', None)
                course_data = client[school].catalog.find_one(
                        {"_id": cid_obj})
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
                "successfully authenticated for this endpoint"}

# /api/<school>/users/<user>/charts
class ListUserCharts(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user):
        charts = client[school].user_charts.find({"user": user})
        if charts is None:
            abort(404, message=f"User {user} has no charts")
        
        return charts.distinct("chart_name") 

# /api/<school>/users/<user>/import
class NewChartResource(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def post(self, school, user):
        userdb = f"{school}-users" 
        user_collection = self.client[userdb][user] 

        command = request.get_json()
        if not ('target' in command and 'destination' in command and 'year' in command):
            abort(400, message=("Copy command malformed. Please send a request "
                'of the form {"target": "target_stock_chart", "destination": '
                '"destination_chart_name"}'))

        target, year, destination = [command['target'], command['year'], command['destination']]

        stock_chart = self.client[school].stock_charts.find({"year": year, "major": target})
        if not stock_chart:
            abort(404, message=("Target chart not found. "
                "Either year is invalid or major does not exist")) 
        
        new_chart = []
        for block in stock_chart:
            del block["major"]
            del block["_id"]
            block["chart_name"] = destination
            new_chart.append(block)

        user_collection.insert_many(new_chart)
        return {"message": "Chart copied successfully"}, 201

# /api/<school>/users/<user>/charts/<chart>
class ChartResource(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, school, user, chart):
        userdb = f"{school}-users" 
        chart = self.client[userdb][user].find({"chart_name": chart})
        if chart is None:
            abort(404, message=f"Chart {chart} does not exist") 

        return dereference_chart_ids(self.client, school, chart) 

    @requires_login
    def post(self, school, user, chart):
        userdb = f"{school}-users" 
        user_collection = self.client[userdb][user] 

        new_chart = response.get_json()
        if type(new_chart) != list:
            abort(400, message=("Please send a list of course objects "
                "you wish to insert into this chart"))

        return new_chart, 201

    @requires_login
    def put(self, school, user, chart):
        userdb = f"{school}-users" 
         

        return new_course, 201

    @requires_login
    def delete(self, school, user, chart):
        userdb = f"{school}-users" 
        collection = self.client[school].user_charts
        collection.deleteMany({"user": user, "chart_name": chart})
        return 200


# /api/<school>/users/<user>/charts/<chart>/<cid>
class CourseResource(Resource):
    def __init__(self, client):
        self.client = client

    @requires_login
    def get(self, user, chart, c_id):
        userdb = f"{school}-users" 

        return CourseManager.courses[user][chart][c_id]

    @requires_login
    def put(self, user, chart, c_id):
        userdb = f"{school}-users" 

        return CourseManager.courses[user][chart][c_id]

    @requires_login
    def delete(self, user, chart, c_id):
        userdb = f"{school}-users" 

        return 200 
