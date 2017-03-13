from flask_restful import Resource 

class UsageResource(Resource):
    def get(self):
        return {"Usage": {
            "/useradd": {
                "POST": {
                    "Requires": "HTTP Basic Authentication describing the username and password for the new user"
                }
            },

            "/authorize": {
                "GET": {
                    "Requires": "HTTP Basic Authentication to authenticate the new user",
                    "Returns": "An API Key for use by non-web-browser clients which is valid for 30 minutes"
                }
            },

            "/logout": {
                "POST": {
                    "Requires": "A browser cookie or an API key for the user session"
                }
            },

            "/delete_user": {
                "POST": {
                    "Requires": "HTTP Basic Authentication to authenticate user one last time"
                }
            },

            "/stock_charts": {
                "GET": {
                    "Returns": "A listing of all available catalog years to find charts for"
                }
            },

            "/stock_charts/<string:year>": {
                "GET": { 
                    "Returns": "A listing of all charts associated with the catalog year <year>"
                    }
                },

            "/stock_charts/<string:year>/<string:major>": {
                "GET": { 
                    "Returns": "The flowchart for <major> for the catalog year <year>"
                    }
                },

            "/<string:user>/charts": {
                "GET": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Returns": "A listing of all charts available for the user"
                }
            },


            "/<string:user>/charts/<string:chart>": {
                "GET": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Returns": "The user's flowchart"
                },
                "POST": {
                    "Requires": "Browser cookie or API key from valid login",
                    "Description": "Create a new flowchart of name <chart>",
                    "Accepts" : "Flowchart in JSON format. Must be sent with application/json content header",
                    "Returns": "The new flowchart",
                    "Note": "Chart cannot exist; if it does, please delete it first."
                    },
                "PUT": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Description": "Append a course to the flowchart",
                    "Accepts" : "Course in JSON format. Must be sent with application/json content header",
                    "Returns": "The course data wrapped with the course ID assigned"
                    },
                "DELETE": {
                    "Requires": "Browser cookie or API key from valid login",
                    "Descripition": "Deletes the flowchart from the server"
                    }
                },

            "/<string:user>/charts/<string:chart>/<int:id>": {
                "GET": {
                    "Requires": "Browser cookie or API key from valid login",
                    "Returns": "The course of id <id>"
                    },
                "PUT": {
                    "Requires": "Browser cookie or API key from valid login",
                    "Description" :"Updates the course at given id",
                    "Accepts" : "Course in JSON format. Must be sent with application/json content header",
                    "Returns": "The new course at given id"
                    },
                "DELETE": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Description": "Deletes the course"
                    }
                }
            }
        }
