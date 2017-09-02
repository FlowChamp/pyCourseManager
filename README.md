# pyCourseManager 0.1
A RESTful server to act as a database for school courses

## Setup
pyCourseManager currently expects a directory layout as follows:

/srv/pyflowchart
├── department_catalogs
│   ├── ...
├── users
│   ├── *username*
│   │   ├── charts
│   │   │   ├── ... 
│   │   └── config
│   ├── ...
└── users.db

Of course in the future most of this will be changeable, but for now... just
give the poor server what it wants!

Also bad design, but within friday.py there is commented out code which will
intialize the users db. It'll eventually be doable with a command line argument
or something.

## Dependencies
- python >= 3.6 (gotta have those formatted strings!)
- python-pymongo
- python-flask
- python-flask-cors
- python-flask-login
- python-flask-restful
- python-flask-sqlalchemy
- python-lxml (for logging in with CAS)
