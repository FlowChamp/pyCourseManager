"""Manage access to course information.

Endpoints:
    /courses                - list departments
    /courses/<dept>         - list all courses within a given department
    /courses/<dept>/<num>   - Get the course by its number within the department 
"""
from flask_restful import Resource, abort
from bson import ObjectId

class DepartmentResource(Resource):
    def __init__(self, client):
        self.db = client.db

    def get(self):
        return {'departments': sorted(self.db.collection_names())}

class DepartmentListingResource(Resource):
    def __init__(self, client):
        self.db = client.db

    def get(self, dept):
        if dept in self.db.collection_names():
            return {'courses': sorted(self.db[dept].distinct('course_number'))}
        else:
            abort(404, message=f"Department {dept} does not exist")

class CatalogCourseResource(Resource):
    def __init__(self, client):
        self.db = client.db

    def get(self, dept, num):
        if dept in self.db.collection_names():
            raw_data = self.db[dept].find_one_or_404({"course_number": num})
            new_dict = {}
            for key,value in raw_data.items():
                if isinstance(value, ObjectId):
                    new_dict[key] = str(value)
                else:
                    new_dict[key] = value
            return new_dict
        else:
            abort(404, message=f"Department {dept} does not exist")

