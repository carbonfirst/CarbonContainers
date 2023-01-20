import sys
import os
import subprocess
import sqlite3
import argparse
import json
# import Pyro4
import config


import socket


def send(comm):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect( (config.HOST, config.PORT) )
            encode = json.dumps(comm).encode("utf-8")
            s.sendall(encode)
    except:
        print("Communication Error")

def send_recv(comm):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect( (config.HOST, config.PORT) )
            encode = json.dumps(comm).encode("utf-8")
            s.sendall(encode)

            resp = s.recv(2048)

        return resp
    except:
        print("Communication Error")

def create(name, template, thresh, policy, lowThresh = 0.4):
    if policy == "wait" or policy == "none":
        create = ["lxc-create", "--name", name, "--template", template]
        container = {"name": name, "settings": {"threshold": thresh, "policy": policy, "status": "idle",  "totals": {"carbon_total": 0, "joules_total": 0}} }
        contCreate = { "command": "create", "cont": container}
        subprocess.Popen(create).communicate()

        send(contCreate)
    
            
    
    elif policy == "replicate":
        createLow = ["lxc-create", "--name", name + "_Low", "--template", template]
        createHigh = ["lxc-create", "--name", name + "_High", "--template", template]

        containerLow = {"name": name + "_Low", "threshold": thresh * lowThresh, "policy": policy, "status": "idle"}
        containerHigh = {"name": name + "_High", "threshold": thresh, "policy": policy, "status": "idle"}
        
    pass

def destroy(name):


    c1 = ["lxc-destroy", "-n", name]

    c2 = ["lxc-destroy", "-n", name + "_Low"]
    c3 = ["lxc-destroy", "-n", name + "_High"]
    

    c1Dest = {"command": "destroy", "name": name}

    subprocess.Popen(c1).communicate()
    send(c1Dest)
    pass

def start(name):

    command = ["lxc-start", "-n", name]
    contStart = {"command": "start", "name": name}
    subprocess.Popen(command).communicate()
    send(contStart)
    pass

def stop(name):

    command = ["lxc-stop", "-n", name]
    contStop = {"command": "stop", "name": name}
    subprocess.Popen(command).communicate()
    send(contStop)
    pass


def freeze(name):
    command = ["lxc-freeze", "-n", name]
    contFreeze = {"command": "freeze", "name": name}
    subprocess.Popen(command).communicate()
    send(contFreeze)


def unfreeze(name):
    command = ["lxc-unfreeze", "-n", name]
    contUnfreeze = {"command": "unfreeze", "name": name}
    subprocess.Popen(command).communicate()
    send(contUnfreeze)


def status(name):
    contStatus = {"command": "status", "name": name}
    resp = send_recv(contStatus)
    print(str(resp))

# TODO: Does -- [command] work? or is that a shell shortcut ignored by python subprocess
def execute(name, comm):
    command = ["lxc-execute", "-n", name, "--", comm]

if __name__ == "__main__":
    pass
    #create("c1", "download", 20, "wait")
    #exit()
    parser = argparse.ArgumentParser(
        description="LXC Carbon Client", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-C", "--command", help="Command")
    parser.add_argument("-N", "--name",  help="Name of container to create") 
    parser.add_argument("-T", "--template", default="download", help="Template to initialize container")
    parser.add_argument("-P", "--policy", default="none", help="Carbon policy; wait, replicate (WiP), migration (WiP")
    parser.add_argument("-R", "--threshold", default="100000000", help="Carbon output threshold (in CO2/ws")
    parser.add_argument("-A", "--args", default="", help="Additional, normal lxc args ")

    args = parser.parse_args()
    if args.command == "create":
        create(args.name, args.template, args.threshold, args.policy)
    elif args.command == "start":
        start(args.name)
    elif args.command == "destroy":
        destroy(args.name)
    elif args.command == "stop":
        stop(args.name)
    elif args.command == "status":
        status(args.name)
# cont = {"name": "c1", "threshold" : 200, "policy": "wait", "status": "idle"}
# cont = {"c1": 20}
# cont = {"c2": 10}

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect( (config.HOST, config.PORT) )
#     encode = json.dumps(cont).encode("utf-8")
#     s.sendall(encode)
