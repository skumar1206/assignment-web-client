#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse
from urllib.parse import urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    #get the code from the server message and return it as an int
    def get_code(self, data):
        split_data = data.split(" ")
        code = split_data[1]
        return int(code)

    #get the headers from the server message and return them
    def get_headers(self,data):
        split_data = data.split("\r\n\r\n")
        mod_data = split_data[0].split("\r\n")
        headers = mod_data[2]
        return headers

    #get the body from the server message and return it
    def get_body(self, data):
        split_data = data.split("\r\n\r\n")
        body = split_data[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Reference 1
        req_url = urlparse(url)
        #empty path case
        if (req_url.path == ""):
            path = "/"
        else:
            path = req_url.path
        #empty port case
        if (req_url.port == None):
            port = 80
        else:
            port = req_url.port
        host = req_url.hostname
        self.connect(host, port)
        #when args is None ( no query params) and generating get request
        if (args == None):
            # Reference 2
            get_req = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(path, host)
        #handling query params and generating get request
        else:
            # Reference 3
            string_args = "?" + urlencode(args)
            # Reference 2
            get_req = "GET {}{} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(path, string_args, host)
        #sending get_req message through socket
        self.sendall(get_req)
        socket = self.socket
        #receing server message
        server_message = self.recvall(socket)
        self.close()

        #retrieving code and body from server message
        code = self.get_code(server_message)
        body = self.get_body(server_message)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Reference 1
        req_url = urlparse(url)
        #empty path case
        if (req_url.path == ""):
            path = "/"
        else:
            path = req_url.path
        #empty port case
        if (req_url.port == None):
            port = 80
        else:
            port = req_url.port
        host = req_url.hostname
        self.connect(host, port)
        #when args is None (no post body) and generating post request
        if (args == None):
            # Reference 4
            post_req = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".format(path, host)
        #when we have the post request body in args, generating post request with it
        else:
            # Reference 3
            string_args = urlencode(args)
            len_args = len(string_args)
            # Reference 4
            post_req = "POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}".format(path, host, len_args, string_args)
        #sending get_req message through socket
        self.sendall(post_req)
        socket = self.socket
        #receing server message
        server_message = self.recvall(socket)
        self.close()

        #retrieving code and body from server message
        code = self.get_code(server_message)
        body = self.get_body(server_message)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
