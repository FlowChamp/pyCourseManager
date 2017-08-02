import json, sys

with open(sys.argv[1], 'r+') as jsonfile:
    try:
        file_courses = json.loads(jsonfile.read())
    except ValueError: 
        sys.exit(1)

    cs = file_courses['courses']
    jsonfile.seek(0)
    jsonfile.write(json.dumps(cs, indent=4))
    jsonfile.truncate()
