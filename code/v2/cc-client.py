import sys
import os
import subprocess
import sqlite3
import argparse
import json
# import Pyro4
import config


import socket

import grpc
import front_pb2
import front_pb2_grpc

# IP = "localhost"
# IP = "198.22.255.30"
# IP = "198.22.255.31"
# IP = "198.22.255.16"
# IP = "198.22.255.26"
# IP = "155.98.38.48"




# IP = "155.98.38.17"
IP = "155.98.39.120"

PORT = 1994

def do_register(name, pol, thresh, status):
   
    with grpc.insecure_channel(str(IP) + ":" + str(PORT)) as c:
        stub = front_pb2_grpc.FrontStub(c)
        # updateResp = stub.Update(order_pb2.UpdateRequest(number=str(number), name=stock, type=buySell, quantity=quantity))
        resp = stub.Register(front_pb2.RegisterRequest(name=name,policy=pol,thresh=thresh,status=status))
        pass

def do_deregister(name):
    print("DEGREG")
    with grpc.insecure_channel(str(IP) + ":" + str(PORT)) as c:
        stub = front_pb2_grpc.FrontStub(c)
        # updateResp = stub.Update(order_pb2.UpdateRequest(number=str(number), name=stock, type=buySell, quantity=quantity))
        resp = stub.Deregister(front_pb2.DeregisterRequest(name=name))
        pass


def do_start(name):
    with grpc.insecure_channel(str(IP) + ":" + str(PORT)) as c:
        stub = front_pb2_grpc.FrontStub(c)
        resp = stub.Start(front_pb2.StartRequest(name=name))


def do_stop(name):
    with grpc.insecure_channel(str(IP) + ":" + str(PORT)) as c:
        stub = front_pb2_grpc.FrontStub(c)
        resp = stub.Stop(front_pb2.StopRequest(name=name))


def do_status(name):
    with grpc.insecure_channel(str(IP) + ":" + str(PORT)) as c:
        stub = front_pb2_grpc.FrontStub(c)
        resp = stub.Status(front_pb2.StatusRequest(name=name))
    
    print(resp.name)
    print(resp.status)

if __name__ == "__main__":



    #do_register("c1","none","0.0", "stopped")
    do_register("c1", "thresh", "1.0", "running")
    # do_register("c1", "none", "1.0", "running")
    #do_deregister("c1")
    # do_start("c1")
    # do_stop("c1")

    # do_status("c1")
    pass
