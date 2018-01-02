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
        """Since in looking for the existence of certain resources this does
        the query already, arg stores the result of that query to pass to the
        function to minimize work done twice"""
        arg = None
        db_name = f"{school}-catalog"

        if db_name not in self.client.database_names():
            abort(404, message=f"No courses database exists for school {school}")
        else:
            arg = school

        if dept:
            depts = self.client[db_name].collection_names()
            if dept not in depts:
                abort(404, message=f"Department {dept} does not exist")
            else:
                arg = self.client[db_name][dept] 

        if num:
            query = self.client[db_name][dept].find({"course_number": num})
            if query.count() == 0:
                abort(404, message=f"Department {dept} does not contain a course numbered {num}")
            elif query.count() != 1:
                abort(500, message=f"Multiple entries for course number {num} under {dept}")
            else:
                arg = query[0] # the course

        return func(self, arg)
    return inner

class FullCatalogResource(Resource):
    def __init__(self, client):
        self.client = client

    def get(self, school):
        courses = []
        for coll in self.client[f"{school}-catalog"].collection_names():
            for crs in self.client[f"{school}-catalog"][coll].find():
                crs["_id"] = str(crs["_id"])
                courses.append(crs)

        return courses

# The check request wrapper handles most of the arguments passed to these functions,
# so the "actual" function only need take one arg (which is given by the wrapper)
class DepartmentResource(Resource):
    def __init__(self, client):
        self.client = client

    @check_request
    def get(self, school):
        return {'departments': sorted(self.client[f"{school}-catalog"].collection_names())}

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
