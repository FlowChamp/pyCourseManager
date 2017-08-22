"""Manage access to course information.

Endpoints:
    /<school>/courses                - list departments
    /<school>/courses/<dept>         - list all courses within a given department
    /<school>/courses/<dept>/<num>   - Get the course by its number within the department 

Notes:
    The check_request checks to see if certain data exists an will abort if it's
    not there -- however, if it needs to query to check for existence why do
    work multiple times? Therefore, the endpoint functions actually mainly take
    the *result* of the check_request queries, and therefore just return its work
"""
from flask_restful import Resource, abort
from bson import ObjectId

def check_request(func):
    def inner(self, school, dept=None, num=None):
        arg = None
        
        if school not in self.client.database_names():
            abort(404, message=f"No database exists for school {school}")
        else:
            arg = school

        if dept:
            depts = self.client[school].catalog.distinct("department")
            if dept not in depts:
                abort(404, message=f"Department {dept} does not exist")
            else:
                arg = self.client[school].catalog.find({"department": dept}) 

        if num:
            query = self.client[school].catalog.find({"department": dept, "course_number": num})
            if query.count() == 0:
                abort(404, message=f"Department {dept} does not contain a course numbered {num}")
            elif query.count() != 1:
                abort(500, message=f"Multiple entries for course number {num} under {dept}")
            else:
                arg = query[0] # the course

        return func(self, arg)
    return inner

class DepartmentResource(Resource):
    def __init__(self, client):
        self.client = client

    @check_request
    def get(self, school):
        return {'departments': sorted(self.client[school].catalog.distinct("department"))}

class DepartmentListingResource(Resource):
    def __init__(self, client):
        self.client = client

    @check_request
    def get(self, courses):
        return {'courses': sorted(courses.distinct("course_number"))}

class CatalogCourseResource(Resource):
    def __init__(self, client):
        self.client = client

    @check_request
    def get(self, course):
        course["_id"] = str(course["_id"])
        return course
