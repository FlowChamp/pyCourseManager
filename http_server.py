#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
from api import CourseResource
 
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
  # GET
  def do_GET(self):
        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send message back to client
        args = [x for x in self.path.split('/') if x is not '']

        if len(args) == 1:
            message = CourseResource.list()
        else:
            message = CourseResource.detail(args[1])
        
        #message = f"You are at {self.path}" 
        # Write content as utf-8 data
        self.wfile.write()

        return
    def parse_url(self):
        args = [x for x in self.path.split('/') if x != '']
 
def run():
  print('starting server...')
 
  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8081)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()
 
 
run()
