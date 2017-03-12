from datetime import datetime, timedelta

from course_manager import CourseManager
from login_manager import LoginManager, login_manager, db
from secret import sqlalchemy_url  

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

## Setup
app = Flask(__name__)
api = Api(app)
CORS(app)

login_manager.init_app(app)
db.init_app(app)

app.config.update(
    SQLALCHEMY_DATABASE_URI = sqlalchemy_url,
    SQLALCHEMY_TRACK_MODIFICATIONS = True,
    SECRET_KEY = 'secret_xxx'
)


## API stuff

# Login resources
api.add_resource(LoginManager.NewUserResource, '/useradd')
api.add_resource(LoginManager.LoginResource,   '/authorize')
api.add_resource(LoginManager.LogoutResource,  '/logout')

api.add_resource(CourseManager.UsageResource,   '/')
api.add_resource(CourseManager.ListStockCharts, '/stock_charts')
api.add_resource(CourseManager.ListUserCharts,  '/<string:user>/charts')
api.add_resource(CourseManager.GetStockChart,   '/stock_charts/<string:major>')
api.add_resource(CourseManager.ChartResource,   '/<string:user>/charts/<string:chart>')
api.add_resource(CourseManager.CourseResource,  '/<string:user>/charts/<string:chart>/<int:c_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4500)

