#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, Randy Wong, Marcin Pietrasik
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
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def urlparser(self, url):
	
        counter = 0
        for i in range(0,len(url)):
            if (url[i] != "/"):
	        counter = counter + 1
	    elif(i == (len(url)-1)):
		    break
            # since we are checking indices in python, need to make sure 
            # we stay in scope to avoid bugs, check if we are first or last 
            # element, and then given that we are a "/" character, if the
            # next or previous element is also a "/" we are together a "//" and
            # can be ignored as we do not show path
            elif((i != 0 or len(url)) and url[i] == "/" and (url[i+1] =="/" or url[i-1] == "/")):
                counter = counter + 1
            else:
                break

	host_port = url[:counter]
	port = 80

	if "http://" in host_port:
            host_port = host_port[7:]
        elif "https://" in host_port:
            host_port = host_port[8:]

	if ":" in host_port:
            host_port = host_port.split(":")
            port = host_port[-1]
            host = ":".join(host_port[:-1])
        else:
	    temp = host_port.split("//")
            host = temp[-1]

	temphost=""
	for letter in host:
	    if letter != "/":
	        temphost += letter
	host= temphost


        # returns tuple of (host, port, path)
	if (url[counter:] == ""):
            return (host, port,"/")
        return (host, port, url[counter:])

    def connect(self, host, port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        return clientSocket

    def get_code(self, data):
        # split on \r\n to get each line of header separate, take first one
        # as it is the one that contains the response code
        data = data.split("\r\n")[0]
        # HTTP response of form HTTP/X.X CODE DESC split on spaces gives
        # [HTTP/X.X, CODE, DESC], returning index 1 gives CODE
        return int(data.split(" ")[1])

    # "\r\n\r\n" shows split between header and body
    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

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
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.urlparser(url)

        # create HTTP Header
        request = "GET " + path + " HTTP/1.1\n"
        request += "Host: " + host + "\n" 
        request += "Connection: close"+"\r\n\r\n"

        clientSocket = self.connect(host, int(port))
        clientSocket.sendall(request)

        response = self.recvall(clientSocket)
        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
        clientSocket.close()

        print(body)

        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        code = 500
        body = ""
	post_body = ""

	if args != None:
	    post_body = urllib.urlencode(args)

        host, port, path = self.urlparser(url)

        # create HTTP Header
        request = "POST " + path + " HTTP/1.1\n"
        request += "Host: " + host + "\n"
	request += "Content-Type: application/x-www-form-urlencoded\n"
	request += "Content-Length:" + str(len(post_body)) + "\n" 
        request += "Connection: close"+"\r\n\r\n"

	request += post_body + "\r\n\r\n"

        clientSocket = self.connect(host, int(port))
        clientSocket.sendall(request)

        response = self.recvall(clientSocket)
        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
        clientSocket.close()

        print(body)

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
        #print( sys.argv[2], sys.argv[1] )
        client.command( sys.argv[2], sys.argv[1] )
        print "program end"
    else:
        #print( sys.argv[1] ) 
        client.command( sys.argv[1] )   
        print "program end"
