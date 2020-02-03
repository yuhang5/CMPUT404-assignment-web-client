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

# Copyright 2020 Yuhang Ma,
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
import urllib.parse
from urllib.parse import urlparse

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

    def get_code(self, data):
        return int(data.split("\r\n")[0].split(" ")[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
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
        # parse url firstly
        #scheme://netloc/path;parameters?query#fragment
        #scheme://host[:port#]/path/…/[?query-string][#anchor]
        parsed_result=urlparse(url)
        net=parsed_result.netloc
        sch=parsed_result.scheme
        #pat=parsed_result.path
        par=parsed_result.params
        que=parsed_result.query
        fra=parsed_result.fragment
        pot=parsed_result.port
        host=parsed_result.hostname
        pat = url.replace(sch+"://"+net,"")
        if len(pat) == 0:
            pat = "/"           
        
        #get port
        if parsed_result.port:
                pot=parsed_result.port
        elif sch == 'http':
                pot=80
        elif sch=='https':
                pot=443    
        # connect
        self.connect(host, pot)        
        
        # do the GET requestion
        reqeust_get = []
        host_line=(str(host)+":"+str(pot))
        reqeust_get.append("GET {} HTTP/1.1".format(pat))
        reqeust_get.append("Host: {}".format(host_line))
        reqeust_get.append("Accept:  */*")
        reqeust_get.append("Connection: close")
        reqeust_get.append("\r\n")
        reqeust_get = "\r\n".join(reqeust_get)
        #print(reqeust_get)
        # send requestion
        self.sendall(reqeust_get)
        # get respone
        response = self.recvall(self.socket)
        self.close()
        code = self.get_code(response)
        body = self.get_body(response)       
        return HTTPResponse(code, body)
    
    def if_args(self, args):
            i_arg=""
            if args is not None:
                i_arg = urllib.parse.urlencode(args)
            return i_arg, len(i_arg)
      
            
            
            
    def POST(self, url, args=None):
        # parse url firstly
        #scheme://netloc/path;parameters?query#fragment
        #scheme://host[:port#]/path/…/[?query-string][#anchor]
        parsed_result=urlparse(url)
        net=parsed_result.netloc
        sch=parsed_result.scheme
        #pat=parsed_result.path
        par=parsed_result.params
        que=parsed_result.query
        fra=parsed_result.fragment
        pot=parsed_result.port
        host=parsed_result.hostname
        
        pat = url.replace(sch+"://"+net,"")
        if len(pat) == 0:
            pat = "/"        
        
        #get port
        if parsed_result.port:
                pot=parsed_result.port
        elif sch == 'http':
                pot=80
        elif sch=='https':
                pot=443            
        # connect
        self.connect(host, pot)
        
        i_arg,Content_Length=self.if_args(args)
        # do the post
        request_post = []
        host_line=(str(host)+":"+str(pot))
        request_post.append("POST {} HTTP/1.1".format(pat))
        request_post.append("Host: {}".format(host_line))
        request_post.append("Content-Type: application/x-www-form-urlencoded")
        request_post.append("Content-Length: {}".format(Content_Length))
        request_post.append("Connection: close")
        request_post.append("\r\n")
        request_post = "\r\n".join(request_post)
        #print("post:\r\n",request_post)  
        #Do args
        request_post = request_post+i_arg
        # send requestion
        self.sendall(request_post)
        # get respones 
        response = self.recvall(self.socket)
        self.close()
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)       
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