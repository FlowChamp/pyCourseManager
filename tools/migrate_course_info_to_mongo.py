import json
import glob
from pymongo import MongoClient

MAJOR_DIR = "/srv/pyflowchart/majors"

def get_json_data(path):
    with open(path, "r") as jsonfile:
        return json.loads(jsonfile.read())

def main():
    client = MongoClient()
    db = client.pycoursemanager

    json_files = glob.glob(MAJOR_DIR + "/*.json")
    json_data = [get_json_data(path) for path in json_files]
    new_json_data = []
    for catalog in json_data:
        found_catalog = False
        dept = None
        course_data = []

        for k,v in catalog.items():
            if not found_catalog:
                dept = k.split()[0]
                found_catalog = True

            # Let's get rid of the department name too, since it's in a collection
            v["course_number"] = int(k[-3:])
            course_data.append(v)

        collection = db[dept]
        collection.insert_many(course_data)


if __name__ == "__main__":
    main()

