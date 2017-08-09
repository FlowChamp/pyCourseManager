from datetime import datetime, timedelta

from course_manager import CourseManager
from login_manager import LoginManager, login_manager, db
import coursedb_manager
from usage_resource import UsageResource
from secret import sqlalchemy_url

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo

## Setup
app = Flask(__name__)
api = Api(app)
CORS(app)

login_manager.init_app(app)

app.config.update(
    SQLALCHEMY_DATABASE_URI = sqlalchemy_url,
    SQLALCHEMY_TRACK_MODIFICATIONS = True,
    SECRET_KEY = 'secret_xxx',
    MONGO_DBNAME = "catalog"
)

mongo = PyMongo(app)
db.init_app(app)
## API stuff

# CourseDB resources
api.add_resource(coursedb_manager.DepartmentResource, '/courses', resource_class_kwargs={'client': mongo})
api.add_resource(coursedb_manager.DepartmentListingResource, '/courses/<string:dept>', resource_class_kwargs={'client': mongo})
api.add_resource(coursedb_manager.CatalogCourseResource, '/courses/<string:dept>/<int:num>', resource_class_kwargs={'client': mongo})

# Login resources
api.add_resource(LoginManager.NewUserResource, '/useradd')
api.add_resource(LoginManager.LoginResource,   '/authorize')
api.add_resource(LoginManager.LogoutResource,  '/logout')
api.add_resource(LoginManager.DeleteUserResource, '/delete_user')

# How to use my lovely program
api.add_resource(UsageResource,   '/')

api.add_resource(CourseManager.ListStockYears,  '/stock_charts')
api.add_resource(CourseManager.ListStockCharts, '/stock_charts/<string:year>')
api.add_resource(CourseManager.ListUserCharts,  '/<string:user>/charts')
api.add_resource(CourseManager.GetStockChart,   '/stock_charts/<string:year>/<string:major>')
api.add_resource(CourseManager.ChartResource,   '/<string:user>/charts/<string:chart>')
api.add_resource(CourseManager.CourseResource,  '/<string:user>/charts/<string:chart>/<int:c_id>')

# @app.before_first_request
# def create_database():
    # db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)

