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

import controller_pb2
import controller_pb2_grpc

from concurrent import futures

import config
import math

from threading import Thread

def nextSmaller(current):
    curCPU = config.MIGRATION_MACHINES[current]["cpu"]
    smallerM = dict( (key,val) for key,val in config.MIGRATION_MACHINES.items() if val["cpu"] < curCPU)
    curMax = 0
    curTarget = current
    for m in smallerM:
        if smallerM[m]["cpu"] > curMax:
            curTarget = m
            curMax = smallerM[m]["cpu"]

    if curTarget != current:
        return curTarget
    else:
        return False

def nextBigger(current):
    curCPU = config.MIGRATION_MACHINES[current]["cpu"]
    largerM = dict( (key,val) for key,val in config.MIGRATION_MACHINES.items() if val["cpu"] > curCPU)
    curMin = math.inf
    curTarget = current
    for m in largerM:

        if largerM[m]["cpu"] < curMin:
            curTarget = m
            curMin = largerM[m]["cpu"]

    if curTarget != current:
        return curTarget
    else:
        return False

class Controller(controller_pb2_grpc.ControllerServicer):

    def __init__(self, host):
        controller_pb2_grpc.ControllerServicer.__init__(self)
        self.ip = host
        pass

    def Migrate(self, request, context):

        # with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
        #     stub = records_pb2_grpc.RecordsStub(c)
        #     resp = stub.Lookup(records_pb2.LookupRequest(name="ALL"))
            
        # self.conts = json.loads(resp.results)

        

        #print("remove remotes")
        # remotes = []
        # for cont in self.conts:
        #     if self.conts[cont]["location"] != self.ip:
        #         remotes.append(cont)

        # for rem in remotes:
        #     del self.conts[rem]

        print("CONTS TO CHECK:")

        self.conts = json.loads(request.conts)
        print(self.conts)

        print("UPDATE STATS")
        for cont in self.conts:
            with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
                stub = records_pb2_grpc.RecordsStub(c)
                resp = stub.Update(records_pb2.UpdateRequest(name=cont, value="status", setts="migrating"))

        print("CHECK")
        t = Thread(target=self.migration,args=() )
        t.start()
        return controller_pb2.MigrateReply(code="1")
    
    def Recieve(self, request, context):

        cont = json.loads(request.cont)
        t = Thread(target=self.migrate_recv, args=(cont,))
        t.start()
        return controller_pb2.RecieveReply(code="1")


    def migration(self):
        if len(self.conts) == 0:
            print("nothing to do")
            return
        for cont in self.conts:
            if self.conts[cont]["policy"].lower() == "none":
                continue
            elif self.conts[cont]["policy"].lower() == "thresh":
                '''
                if throttled and below thresh
                    size up
                elif carbon exceeded
                    size down
                elif nextusage < (nextSmallerCPU / curCPU)*100
                    size down
                '''

                cpu = self.conts[cont]["current"]["cpu"]
                carb = self.conts[cont]["current"]["carbon"]
                thresh = self.conts[cont]["threshold"]
                curMach = config.MIGRATION_MACHINES[self.conts[cont]["location"]]
                if cpu == curMach["cpu"]*100 and carb < thresh:
                    target = nextBigger(curMach["host"])
                    if target:
                        print("Migrate to " + str(target))
                    pass

                elif carb > thresh:
                    target = nextSmaller(curMach["host"])
                    if target:
                        print("Migrate to " + str(target))
                        self.migrate_send(cont,target)
                    pass
                
                elif cpu <= (curMach["cpu"] / nextSmaller(curMach["host"]))*100:
                    
                    target = nextSmaller(curMach["host"])
                    if target:
                        print("Migrate to " + str(target))
                    pass
                
                pass
                pass
            elif self.conts[cont]["policy"].lower() == "target":
                '''
                if throttled and below target
                    size up
                elif carbon exceeded
                    size down
                '''
                cpu = self.conts[cont]["current"]["cpu"]
                carb = self.conts[cont]["current"]["carbon"]
                thresh = self.conts[cont]["threshold"]
                curMach = config.MIGRATION_MACHINES[self.conts[cont]["location"]]
                
                if cpu == float(curMach["cpu"]*100) and carb < float(thresh):
                    print("SIZE UP")
                    target = nextBigger(curMach["host"])
                    if target:
                        print("Migrate to " + str(target))
                        self.migrate_send(cont,target) 
                    pass

                elif carb > float(thresh):
                    print("SIZE DOWN")
                    target = nextSmaller(curMach["host"])
                    if target:
                        print("Migrate to " + str(target))
                    pass

                
                pass

        pass
    def migrate_target(self,current, scale_down):
        

        if scale_down:
            target = nextSmaller(current)
        else:
            target = nextBigger(current)

        return target
    

    def migrate_send(self, contName, target):

        if os.path.exists(config.WORKING_DIR + "/checkpoint_"+str(contName)):
            os.rmdir(config.WORKING_DIR + "/checkpoint_"+str(contName))

        print("Make check dir")
        #os.mkdir(config.WORKING_DIR + "/checkpoint_"+str(contName))
        os.mkdir("/var/lib/lxc/"+str(contName)+"/check")

        print("lxc-check")
        checkpoint = ["lxc-checkpoint", "-s", "-D", "/var/lib/lxc/"+str(contName)+"/check", "-n", contName]
        subprocess.Popen(checkpoint).communicate()

        print("Copy Container Dict")
        copyContDir = ["cp", "-r", "/var/lib/lxc/"+str(contName), config.WORKING_DIR]
        subprocess.Popen(copyContDir).communicate()

        #print("Move Check into container dir")
        #move = ["mv", config.WORKING_DIR + "/checkpoint_"+str(contName), config.WORKING_DIR + "/" + str(contName) ]
        #subprocess.Popen(move).communicate()



        #print("tar container fs")
        #tarCont = ["tar", "--numeric-owner", "-czvf", str(contName)+".tar.gz", "./*"]
        #subprocess.Popen(tarCont).communicate()

        print("zip")
        zipCont = ["zip", "-r", config.WORKING_DIR+"/"+str(contName)+".zip", config.WORKING_DIR+"/"+str(contName)]
        subprocess.Popen(zipCont).communicate()
    
        
        print("scp filesystem")
        scp = ["scp", "-i", config.SSH_KEY_PATH, config.WORKING_DIR+"/"+str(contName) + ".zip", config.SSH_USER+"@"+target+":"+config.WORKING_DIR]
        subprocess.Popen(scp).communicate()
        
        #os.chdir(config.WORKING_DIR)

        print("destroy old")
        destroyOldCont = ["lxc-destroy", str(contName)]
        subprocess.Popen(destroyOldCont).communicate()
        rm1 = ["rm", "-r", config.WORKING_DIR+"/"+str(contName)]
        rm2 = ["rm", config.WORKING_DIR+"/"+str(contName)+".zip"]
        subprocess.Popen(rm1).communicate()
        subprocess.Popen(rm2).communicate()


        with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
            stub = records_pb2_grpc.RecordsStub(c)
            resp = stub.Update(records_pb2.UpdateRequest(name=contName, value="location", setts=target))
                
        with grpc.insecure_channel( target +":" + config.CONTROLLER_PORT) as c:
            stub = controller_pb2_grpc.ControllerStub(c)
            resp = stub.Recieve(controller_pb2.RecieveRequest(cont=contName))

    
        # self.conts[contName]["status"] = "remote @ " + str(target)

        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.connect( (target, config.MIGRATION_PORT) )
        #     encode = json.dumps({contName: self.conts[contName]}).encode("utf-8")
        #     s.sendall(encode)


        pass


   
    def migrate_recv(self, name):
       
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    
        #     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #     s.bind( (self.host, config.MIGRATION_PORT) )
        #     # print("listening")
        #     s.listen(1)
        #     conn, addr = s.accept()
            # with conn:
                # data = conn.recv(2048)
                # cont = json.loads(data.decode("utf-8"))

                # name = list(cont.keys())[0]

        print("unzip")
        unzip = ["unzip", config.WORKING_DIR+"/"+str(name)+".zip", "-d", config.WORKING_DIR ]
        print(unzip)
        subprocess.Popen(unzip).communicate()

        print("relocate")
        move = ["mv", config.WORKING_DIR+config.WORKING_DIR+"/"+str(name), "/var/lib/lxc"]
        subprocess.Popen(move).communicate()

        print("restore")
        restart = ["lxc-checkpoint", "-r", "-D", "/var/lib/lxc/"+str(name)+"/check", "-n", str(name)]
        subprocess.Popen(restart).communicate()
        # self.conts[cont[""]]

        print("cleanup")
        cleanup1 = ["rm", config.WORKING_DIR+"/"+str(name)+".zip"]
        cleanup2 = ["rm", "-r", "/var/lib/lxc/"+str(name)+"/check"]
        cleanup3 = ["rm", "-r", config.WORKING_DIR+"/users"]

        subprocess.Popen(cleanup1).communicate()
        subprocess.Popen(cleanup2).communicate()
        subprocess.Popen(cleanup3).communicate()

        print("done")

        #with grpc.insecure_channel("localhost:" + config.RECORD_PORT) as c:
        #    stub = records_pb2_grpc.RecordsStub(c)
        #    resp = stub.Update(records_pb2.UpdateRequest(name=contName, value="ALL", setts=))
        # self.conts[name] = cont[name]

def run(ip, port):
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=5),maximum_concurrent_rpcs=5)
    # order_pb2_grpc.add_OrderServicer_to_server(Order(mode), server)
    # front_pb2_grpc.add_FrontServicer_to_server(Front(), server)
    # records_pb2_grpc.add_RecordsServicer_to_server(Records(), server)
    controller_pb2_grpc.add_ControllerServicer_to_server(Controller(ip), server)
    server.add_insecure_port("[::]:"+str(port))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    ip = sys.argv[1]
    port = config.CONTROLLER_PORT

    run(ip,port)
