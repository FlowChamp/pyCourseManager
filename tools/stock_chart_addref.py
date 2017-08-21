import json
import glob
import os

from pymongo import MongoClient
from migrate_course_info_to_mongo import MAJOR_DIR, get_json_data

STOCK_DIR = "/srv/pyflowchart/stock_charts/15-17"

def main():
    client = MongoClient()
    db = client.cpslo
    catalog_coll = db.catalog 
    stock_coll = db.stock_charts 

    json_files = glob.glob(STOCK_DIR + "/*.json")

    for fn in json_files:
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
                    obj = catalog_coll.find_one({"department": dept, "course_number": int(idf)})
                    if not obj:
                        print("No object found")
                        continue
                    else:
                        ids.append(obj["_id"])

                course_data["catalog_id"] = ids 

            elif " or " in catalog_id:
                if len(catalog_id.split(" ")) == 4:
                    options = catalog_id.split(" or ")
                    dept, num1 = options[0].split(" ")
                    num2 = options[1]

                    course_data["type"] = "option"
                    ids = []

                    for idf in [num1, num2]:
                        obj = catalog_coll.find_one({"department": dept, "course_number": int(idf)})
                        if not obj:
                            print("No object found")
                            continue
                        else:
                            ids.append(obj["_id"])

                    course_data["catalog_id"] = ids

                # Must be D1 N1 or D2 N2
                else:
                    ids = []
                    d1n1, d2n2 = catalog_id.split(" or ")
                    d1, n1 = d1n1.split(" ")
                    d2, n2 = d2n2.split(" ")
                    for i in range(2):
                        dept = [d1, d2][i]
                        idf = [n1, n2][i]
                        obj = catalog_coll.find_one({"department": dept, "course_number": int(idf)})
                        if not obj:
                            print("No object found")
                            continue
                        else:
                            ids.append(obj["_id"])

                    course_data["catalog_id"] = ids 

            elif "/" in catalog_id:
                dept, nums = catalog_id.split(' ')
                num1, num2 = nums.split("/")

                course_data["type"] = "coreq"
                ids = []

                for idf in [num1, num2]:
                    obj = catalog_coll.find_one({"department": dept, "course_number": int(idf)})
                    if not obj:
                        print("No object found")
                        continue
                    else:
                        ids.append(obj["_id"])

                course_data["catalog_id"] = ids 

            elif catalog_id == "" or catalog_id.isspace():
                course_data["elective_title"] = course_data["title"]
                course_data["type"] = "elective"
                pause = True

            else:
                course = course_data["catalog"].split(" ")
                if len(course) == 2:
                    dept, number = course
                    obj = catalog_coll.find_one({"department": dept, "course_number": int(number)})
                    if not obj:
                        continue
                    else:
                        course_data["catalog_id"] = obj['_id']
                else:
                    continue
                
            for key in ["title", "prereqs", "credits", "catalog"]:
                del course_data[key]

            course_data["flags"] = []
            # course_data["school"] = "cpslo"
            
            chart_name = fn 
            chart_name = chart_name.split("/")[-1]
            chart_name = chart_name.strip(".json")
            chart_name = chart_name.replace("_", " ")
            
            course_data["major"] = chart_name

            courses.append(course_data)

        stock_coll.insert_many(courses) 

if __name__ == "__main__":
    main()

