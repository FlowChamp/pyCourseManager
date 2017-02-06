#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler): 
    def __init__(self, req, addr, ser):
        BaseHTTPRequestHandler.__init__(self, req, addr, ser)
        print("Jim")
    
    def _set_headers(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

    # GET
    def do_GET(self):
        self._set_headers()
        
        # print(self.string)

        # json_data = json.dumps(self.my_data)
        # json_bytes = str.encode(json_data)
        # message = json_bytes 

        # message = f"You are at {self.path}" 
        # Write content as utf-8 data
        # self.wfile.write(message)

        # return

    def do_POST(self):
        self._set_headers()

        length = int(self.headers['content-length'])
        raw_data = self.rfile.read(length)
        raw_data = str(raw_data, 'utf-8')
        # self.my_data = json.loads(raw_data)
        # print(self.string)
        # self.string += "my"
        # print(self.string)

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
