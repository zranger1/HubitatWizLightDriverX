#!/usr/bin/env python3
import sys
import json
import time
import socket

from twisted.python import log
from twisted.web import server
from twisted.web.resource import Resource
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, endpoints

##############################################
# Constants and global objects
##############################################
HTTP_PORT = 8000
POLLING_INTERVAL = 3600  # one hour 
BROADCAST_IP = "192.168.1.255"
LightList = {}
LightEnumerators = []

##############################################
# Enumerator for Wiz bulbs -- broadcasts a
# registration datagram and listens for responses
##############################################
class WizEnumerator(DatagramProtocol):
    
    WIZ_COMMAND_PORT = 38899
    
    def __init__(self):
        global reactor
        # listen on Wiz command port
        reactor.listenUDP(self.WIZ_COMMAND_PORT, self)
        self.transport.socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)        
    
    def datagramReceived(self, data, host):
        global LightList
        
        if (b'result' in data):      
            payload = json.loads(data.decode('utf8'))
            mac = payload["result"]["mac"]          
            LightList[mac.lower()] = host[0]               
            
# send broadcast datagram to enumerate all Wiz lights on the network   
    def queryLights(self) :
        print("  enumerator: Wiz")
        self.transport.write(b'{"params":{"phoneIp":"127.0.0.0","phoneMac":"BEEFDEADBEEF","register":true},"id":10,"method":"registration"}',(BROADCAST_IP, self.WIZ_COMMAND_PORT))                 
                    
##############################################
# Classes for web service
##############################################
class WebRoot(Resource):
    isLeaf = False
    
    def getChild(self,name, request):
        if name == '':
            return self
        return Resource.getChild(self, name, request)
    
    def render_GET(self, request):
        return(b"ok")
    
# refresh the list of available lights
class StopAndExit(WebRoot):
    isLeaf = True
    
    def render_GET(self, request):
        global reactor
       
        print("Stop requested")
        reactor.stop()
        return(b'{"result":true}')   
    
# refresh the list of available lights
class RefreshLightList(WebRoot):
    isLeaf = True
    
    def render_GET(self, request):
       
        print("Refresh requested")
        enumerateLights()
        return(b'{"result":true}')
    
# return the list of available lights as a json object
class GetLightList(WebRoot):
    isLeaf = True
    
    def render_GET(self, request):
        global LightList
        
        print("List requested")
        msg = json.dumps(LightList,separators=(',', ':'))
        return(msg.encode('utf-8'))
   
# handle http GET requests to map a known MAC
# to its current ip address    
class QueryMac(WebRoot):
    isLeaf = True
    ip = '{"ip":"not found","result": false}'

    def render_GET(self, request):
        global LightList
        print("resolve :",request)        
        
        jsonOut = {}       
        try:
            mac = request.args[b'mac'][0].decode()
            mac = mac.lower()
            if (mac in LightList):             
                jsonOut["ip"] = LightList[mac]
                jsonOut["result"] = True
            else:
                jsonOut["ip"] = "not found"
                jsonOut["result"] = False
        except Exception as blarf:
            template = "Unhandled exception. Type: {0},  Args:\n{1!r}"
            message = template.format(type(blarf).__name__, blarf.args)
            print(message)            
            jsonOut["ip"] = "invalid request"
            jsonOut["result"] = False
                   
        msg = json.dumps(jsonOut,separators=(',', ':'))
        return(msg.encode('utf-8'))
    
##############################################
# get list of light ip and mac addresses for
# all installed protocols.
##############################################
def enumerateLights():
    global LightEnumerators
    
    print("enumerateLights at", time.asctime())
    
    for i in LightEnumerators :
        i.queryLights()           
    
##############################################
# Main 
##############################################    
# set up http endpoints    
root = WebRoot()
root.putChild(b'resolve',QueryMac())
root.putChild(b'refresh',RefreshLightList())
root.putChild(b'list',GetLightList())
root.putChild(b'stop',StopAndExit())

# fire up the web service
site = server.Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, HTTP_PORT)
endpoint.listen(site)

# start the light enumerator
LightEnumerators = [WizEnumerator()]
lc = LoopingCall(enumerateLights)
lc.start(POLLING_INTERVAL)
    
# run event loop
reactor.run()