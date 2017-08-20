import json
import glob
import os

from pymongo import MongoClient
from migrate_course_info_to_mongo import MAJOR_DIR, get_json_data

STOCK_DIR = "/srv/pyflowchart/stock_charts/15-17"

def main():
    client = MongoClient()
    catalog_db = client.catalog
    stock_collection = client.stock_charts

    json_files = glob.glob(STOCK_DIR + "/*.json")
    # This is a list of all stock charts
    json_data = [get_json_data(path) for path in json_files]

    for _,course_data in json_data[0].items():
        obj_id = None
        course = course_data["catalog"].split(" ")
        if len(course) == 2:
            dept, number = course
            obj = catalog_db[dept].find_one({"course_number": int(number)})
            if not obj:
                continue
        else:
            continue
            
        for key in ["title", "prereqs", "credits", "catalog"]:
            del course_data[key]

        course_data["catalog_id"] = str(obj['_id'])
        course_data["department"] = dept
        course_data["flags"] = []
        course_data["color"] = []
        print(course_data)
        input()
                
if __name__ == "__main__":
    main()







