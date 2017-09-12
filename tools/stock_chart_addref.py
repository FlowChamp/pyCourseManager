import json
import glob
import os

from pymongo import MongoClient
from migrate_course_info_to_mongo import MAJOR_DIR, get_json_data

STOCK_DIR = "/srv/pyflowchart/stock_charts/15-17"

def main():
    client = MongoClient()
    db = client["cpslo-stockcharts_15-17"]
    catalog_db = client["cpslo-catalog"]

    json_files = glob.glob(STOCK_DIR + "/*.json")

    # Each file is its own collection
    for fn in json_files:
        chart_name = os.path.basename(fn).strip(".json")

        collection = db[chart_name]

        chart_data = get_json_data(fn)
        courses = []
        
        for _,course_data in chart_data.items():
            pause = False
            catalog_id = course_data["catalog"]

            if ", or " in catalog_id:
                idfs = catalog_id.split(", ")
                idfs[-1] = idfs[-1].replace("or ", '')
                dept, num1 = idfs[0].split(" ")
                idfs[0] = num1

                course_data["type"] = "option"
                ids = []
                for idf in idfs:
                    obj = catalog_db[dept].find_one({"course_number": int(idf)})
                    if not obj:
                        print("No object found")
                        continue
                    else:
                        ids.append(obj["_id"])

                course_data["catalog_id"] = ids
                course_data["department"] = dept

            elif " or " in catalog_id:
                if len(catalog_id.split(" ")) == 4:
                    options = catalog_id.split(" or ")
                    dept, num1 = options[0].split(" ")
                    num2 = options[1]

                    course_data["type"] = "option"
                    ids = []

                    for idf in [num1, num2]:
                        obj = catalog_db[dept].find_one({"course_number": int(idf)})
                        if not obj:
                            print("No object found")
                            continue
                        else:
                            ids.append(obj["_id"])

                    course_data["catalog_id"] = ids
                    course_data["department"] = dept

                # Must be D1 N1 or D2 N2
                else:
                    depts = []
                    ids = []
                    d1n1, d2n2 = catalog_id.split(" or ")
                    d1, n1 = d1n1.split(" ")
                    d2, n2 = d2n2.split(" ")
                    for i in range(2):
                        dept = [d1, d2][i]
                        idf = [n1, n2][i]
                        obj = catalog_db[dept].find_one({"course_number": int(idf)})
                        if not obj:
                            print("No object found")
                            continue
                        else:
                            ids.append(obj["_id"])
                        depts.append(dept)

                    course_data["catalog_id"] = ids 
                    course_data["department"] = depts

            elif "/" in catalog_id:
                dept, nums = catalog_id.split(' ')
                num1, num2 = nums.split("/")

                course_data["type"] = "coreq"
                ids = []

                for idf in [num1, num2]:
                    obj = catalog_db[dept].find_one({"course_number": int(idf)})
                    if not obj:
                        print("No object found")
                        continue
                    else:
                        ids.append(obj["_id"])

                course_data["catalog_id"] = ids 
                course_data["department"] = dept

            elif catalog_id == "" or catalog_id.isspace():
                course_data["elective_title"] = course_data["title"]
                course_data["type"] = "elective"
                pause = True

            else:
                course = course_data["catalog"].split(" ")
                if len(course) == 2:
                    dept, number = course
                    obj = catalog_db[dept].find_one({"course_number": int(number)})
                    if not obj:
                        continue
                    course_data["catalog_id"] = obj['_id']
                    course_data["department"] = dept
                else:
                    course_data["type"] = "general_ed"
                
            for key in ["title", "prereqs", "credits", "catalog"]:
                del course_data[key]

            course_data["flags"] = []

            courses.append(course_data)

        collection.insert_many(courses) 

if __name__ == "__main__":
    main()

