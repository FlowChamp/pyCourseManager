"""Manage access to course information.

Endpoints:
    /courses                - list departments
    /courses/<dept>         - list all courses within a given department
    /courses/<dept>/<num>   - Get the course by its number within the department 
"""
from flask import request
from flask_restful import Resource, abort
import json, os

coursedb_root = "/srv/pyflowchart/majors"

known_catalog = {}

for department_file in os.listdir(coursedb_root):
    department_idf = department_file.split('_')[0].upper()
    path = f"{coursedb_root}/{department_file}"
    with open(path, 'r') as jsonfile:
        try:
            file_courses = json.loads(jsonfile.read())
        except ValueError: 
            print(f"JSON file {path} invalid or corrupt.")
            continue

    known_catalog[department_idf] = file_courses

class DepartmentResource(Resource):
    def get(self):
        return {'departments': list(known_catalog)}

class DepartmentListingResource(Resource):
    def get(self, dept):
        if dept in known_catalog:
            return {'courses': list(known_catalog[dept])}
        else:
            abort(404, message=f"Department {dept} does not exist")

class CatalogCourseResource(Resource):
    def get(self, dept, num):
        if dept in known_catalog:
            idf = f"{dept} {num}"
            if idf in known_catalog[dept]:
                return known_catalog[dept][idf]
            else:
                abort(404, message=(f"Course {idf} does not exist "
                        f"within department {dept}"))
        else:
            abort(404, message=f"Department {dept} does not exist")
        

