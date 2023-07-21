import sys
import os
import subprocess
import sqlite3
import argparse
import threading
import time
import socket
import json
import pickle
import re
from multiprocessing import Process, Queue

from daemon3x import daemon

import grpc
import front_pb2
import front_pb2_grpc

import records_pb2
import records_pb2_grpc

from concurrent import futures

import config
import time

class Records(records_pb2_grpc.RecordsServicer):

    def __init__(self):
        records_pb2_grpc.RecordsServicer.__init__(self)

        if os.path.exists("./conts.json"):
                with open(config.RECORD_FILE, "r") as f:
                    cat = f.read()
                    self.records = json.loads(cat)
        
        else:
             self.records = dict()
        

    def Lookup(self, request, context):
         name = request.name

         if name == "ALL":
              resp = json.dumps(self.records)
              return records_pb2.LookupReply(results=resp)
         elif name in self.records:
              resp = json.dumps({name: self.records[name]})
              return records_pb2.LookupReply(results=resp)
         pass
    

    def Update(self,request,context):
        name = request.name
        value = request.value
        setts = request.setts
        print("SETTS")
        print(setts)
        if setts == "delete" and name in self.records:
             del self.records[name]
        
        if setts != "delete" and value == "ALL":     
            setts = json.loads(request.setts)
            self.records[name]=setts
        
        if setts != "delete" and value != "ALL" and name in self.records:
             self.records[name][value] = setts

        with open(config.RECORD_FILE, "w") as f:
             dump = json.dumps(self.records)
             f.write(dump)
        return records_pb2.UpdateReply(code="1")
        pass



def run(ip, port):
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=5),maximum_concurrent_rpcs=5)
    # order_pb2_grpc.add_OrderServicer_to_server(Order(mode), server)
    # front_pb2_grpc.add_FrontServicer_to_server(Front(), server)
    records_pb2_grpc.add_RecordsServicer_to_server(Records(), server)
    server.add_insecure_port("[::]:"+str(port))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    ip = config.RECORD_IP
    port = config.RECORD_PORT

    run(ip, port)
    
