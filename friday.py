from datetime import datetime, timedelta

from course_manager import CourseManager
from login_manager import LoginManager, login_manager, db
import coursedb_manager
from usage_resource import UsageResource
from secret import sqlalchemy_url
from login import LoginResource

from flask import Flask
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

## Setup
app = Flask(__name__)
api = Api(app)

login_manager.init_app(app)

app.config.update(
    SQLALCHEMY_DATABASE_URI = sqlalchemy_url,
    SQLALCHEMY_TRACK_MODIFICATIONS = True,
    SECRET_KEY = 'secret_xxx',
)

db.init_app(app)

mongo = MongoClient()

## API stuff
API_PREFIX = "/api"

# CourseDB resources
api.add_resource(coursedb_manager.DepartmentResource, 
    f'{api}/<string:school>/courses',
    resource_class_kwargs={'client': mongo}
    )
api.add_resource(coursedb_manager.DepartmentListingResource, 
    f'{api}/<string:school>/courses/<string:dept>',
    resource_class_kwargs={'client': mongo}
    )
api.add_resource(coursedb_manager.CatalogCourseResource, 
    f'{api}/<string:school>/courses/<string:dept>/<int:num>',
    resource_class_kwargs={'client': mongo}
    )

# Login resources
api.add_resource(LoginResource,   f'{api}/<string:school>/authorize')
api.add_resource(LoginManager.LogoutResource,  f'{api}/logout')

# How to use my lovely program
api.add_resource(UsageResource,   f'{api}/')

api.add_resource(CourseManager.ListStockYears,  
    f'{api}/<string:school>/stock_charts',
    resource_class_kwargs={'client': mongo}
    )
api.add_resource(CourseManager.ListStockCharts, 
    f'{api}/<string:school>/stock_charts/<string:year>',
    resource_class_kwargs={'client': mongo}
    )

api.add_resource(CourseManager.GetStockChart,   
    f'{api}/<string:school>/stock_charts/<string:year>/<string:major>',
    resource_class_kwargs={'client': mongo}
    )

api.add_resource(CourseManager.ListUserCharts,  f'{api}/<string:user>/charts')
api.add_resource(CourseManager.ChartResource,   f'{api}/<string:user>/charts/<string:chart>')
api.add_resource(CourseManager.CourseResource,  f'{api}/<string:user>/charts/<string:chart>/<int:c_id>')

# @app.before_first_request
# def create_database():
    # db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)

