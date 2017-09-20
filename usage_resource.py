from flask_restful import Resource 

class UsageResource(Resource):
    def get(self):
        return {"Usage": {
            "/api/<string:school>/authorize": {
                "GET": {
                    "Requires": "HTTP Basic Authentication to authenticate the new user",
                    "Returns": "The users's saved configuration"
                },

                "POST": {
                    "Requires": "HTTP Basic Authentication to authenticate the new user",
                    "Description": "Authorize the user, and optionally be remembered for a year",
                    "Accepts" : 'Any object with a "remember" key (the value is arbitrary)',
                    "Returns": "The users's saved configuration"
                }
            },

            "/api/<string:school>/users/<string:user>/logout": {
                "POST": {
                    "Requires": "A cookie for the user session"
                }
            },

            "/api/<string:school>/stock_charts": {
                "GET": {
                    "Returns": """A listing of all available catalog years
                    to find charts for at the given <school>"""
                }
            },

            "/api/<string:school>/stock_charts/<string:year>": {
                "GET": { 
                    "Returns": """A listing of all charts associated 
                    with the catalog year <year> at the given <school>"""
                    }
                },

            "/api/<string:school>/stock_charts/<string:year>/<string:major>": {
                "GET": { 
                    "Returns": """The flowchart for <major> for the catalog
                    year <year> at the given <school>"""
                    }
                },

            "/api/<string:school>/users/<string:user>/import": {
                "POST": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Accepts": """A JSON description of the chart the user wishes 
                        to import in the format {'target': target_stock_chart, 
                        'year': chart_year, 'destination': user_specified_name}"""
                }
            },

            "/api/<string:school>/users/<string:user>": {
                "GET": { 
                    "Requires": "A valid login cookie",
                    "Returns": "The login status of the specified user"
                }
            },
            
            "/api/<string:school>/users/<string:user>/config": {
                "GET": { 
                    "Requires": "Cookie from valid login",
                    "Returns": "The user's saved config"
                },
                "POST": {
                    "Requires": "Cookie from valid login",
                    "Description": "Replace the config in the database with the sent config",
                    "Accepts" : "The users's new config",
                    "Returns": "A success message",
                }
            },

            "/api/<string:school>/users/<string:user>/charts": {
                "GET": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Returns": "A listing of all charts available for the user"
                }
            },


            "/api/<string:school>/users/<string:user>/charts/<string:chart>": {
                "GET": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Returns": "The user's flowchart"
                },
                "POST": { 
                    "Requires": "Browser cookie or API key from valid login",
                    "Description": "Append a course to the flowchart",
                    "Accepts" : "Course in JSON format. Must be sent with application/json content header",
                    "Returns": "The course ID, accessible by the returned object's '_id' key"
                    },
                "DELETE": {
                    "Requires": "Browser cookie or API key from valid login",
                    "Descripition": "Deletes the flowchart from the server"
                    }
                },

            "/api/<string:school>/users/<string:user>/charts/<string:chart>/<string:id>": {
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
                },

            "/api/<string:school>/courses": {
                "GET": {
                    "Returns": "A list of available departments"
                    }
                },
            "/api/<string:school>/courses/<string:dept>": {
                "GET": {
                    "Returns": "A list of all courses within a given department"
                    }
                },

            "/api/<string:school>/courses/<string:dept>/<int:num>": {
                "GET": {
                    "Returns": "The course associated with the number in the department"
                    }
                }
            }
        }
