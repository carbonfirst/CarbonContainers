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


# import daemon
# import lockfile

import config


class Front(front_pb2_grpc.FrontServicer):
    def __init__(self, host):
        front_pb2_grpc.FrontServicer.__init__(self)
        self.conts = dict()
        self.ip = host
    
    def Register(self, request, context):
        print("REGISTER")
        name = request.name
        policy = request.policy
        thresh = request.thresh
        status = request.status.lower()

        #newCont = {"name":name, "policy":policy, "threshold":thresh, "status":status, "location": ip, "totals": {"carbon_total": 0, "joules_total": 0}}
        newCont = {"name":name, 
                   "policy":policy, 
                   "threshold":float(thresh),
                    "status":status, 
                    "location": ip, 
                    "cpu_cores": config.MIGRATION_MACHINES[str(self.ip)]["cpu"],
                    "current": {"carbon": 0, "joules":0, "cpu":0}, 
                    "totals": {"carbon_total": 0, "joules_total": 0}
                    }
        mesg = json.dumps(newCont)

        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="ALL", setts=mesg))
            pass

        return front_pb2.RegisterReply(code="1")


    def Deregister (self, request, context):
        name = request.name
        print("DEREGISTER")
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="ALL", setts="delete"))
            pass
        return front_pb2.DeregisterReply(code="1")
        pass

    def Start (self, request, context):
        name = request.name
        command = ["lxc-start",  "-n", name]
        subprocess.Popen(command).communicate()
        print("START")
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="status", setts="running"))
            pass
        pass
        return front_pb2.StartReply(code="1")
    
    def Stop (self, request, context):
        print("STOP")
        name = request.name
        print(name)
        command = ["lxc-stop" ,"-n",str(name).strip()]
        # command = "lxc-stop -n " + str(name).strip()
        subprocess.Popen(command).communicate()
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="status", setts="stopped"))
        pass

        return front_pb2.StopReply(code="1")
    def Freeze (self, request, context):
        name = request.name
        command = "lxc-freeze -n " + name
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="status", setts="frozen"))
        pass
    def Unfreeze (self, request, context):
        name = request.name
        command = "lxc-unfreeze -n " + name
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="status", setts="running"))
        pass
    def Status (self, request, context):
        name = request.name
        
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Lookup(records_pb2.LookupRequest(name=name))
            # print(resp.results)
        pass
        if name == "ALL":
            return front_pb2.StatusReply(name=name, status=resp.results)
        else:
            stats = json.loads(resp.results)
            stats = stats[name]
            stats = json.dumps(stats)
            return front_pb2.StatusReply(name=name, status=stats)
        
    def Policy (self, request, context):
        name = request.name
        policy = request.policy
        thresh = request.thresh
        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="policy", setts=policy))
            resp = stub.Update(records_pb2.UpdateRequest(name=name, value="thresh", setts=thresh))
        pass
    
class FrontDaemon(daemon):
    def __init__(self, pidfile, ip, port):
        self.conts = {}
        
        super().__init__(pidfile)
        self.ip = ip
        self.port = port

        
  
    def run(self):
        server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=5),maximum_concurrent_rpcs=5)
        # order_pb2_grpc.add_OrderServicer_to_server(Order(mode), server)
        front_pb2_grpc.add_FrontServicer_to_server(Front(), server)
        server.add_insecure_port("[::]:"+str(self.port))
        server.start()
        server.wait_for_termination()

def run(ip, port):
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=5),maximum_concurrent_rpcs=5)
    # order_pb2_grpc.add_OrderServicer_to_server(Order(mode), server)
    front_pb2_grpc.add_FrontServicer_to_server(Front(ip), server)
    server.add_insecure_port("[::]:"+str(port))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    # ip = config.FRONT_IP
    port = config.FRONT_PORT

    ip = str(sys.argv[1])
    run(ip, port)
    
    # d = FrontDaemon(config.WORKING_DIR + "/front.pid", ip, port)

    # if sys.argv[1] == "start":
    #     d.start()
    
    # elif sys.argv[1] == "stop":
    #     d.stop()

    # sys.exit(0)
