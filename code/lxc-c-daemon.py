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


# import daemon
# import lockfile

import config


events = ["task-clock", "context-switches", "cpu-migrations", "page-faults", "cycles", "instructions", "branches", "branch-misses"]        


class LXC_C_Daemon(daemon):

    def __init__(self, pidfile):
        self.conts = {}
        
        super().__init__(pidfile)
        host = ["hostname", "-I"]

        hosts = subprocess.Popen(host, stdout=subprocess.PIPE).communicate()[0]

        hosts = hosts.split()

        self.host = hosts[1]
        
    
    def run(self):
        try:
            t1 = threading.Timer(1.0, self.check_carbon)
            t2 = threading.Timer(1.0, self.listen)
            t3 = threading.Timer(1.0, self.procMonitor)
            t4 = threading.Timer(1.0, self.migrate_recv)

            t1.start()
            t2.start()
            t3.start()

        except Exception as ex:

            with open(config.WORKING_DIR + "/run_excep.log", "w") as f:
                f.write(str(ex))

    # Listen for lxc-c commands from client
    def listen(self):
        try:
            while True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind( (config.HOST, config.PORT) )
                    s.listen(1)
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(2048)
                        command = json.loads(data.decode("utf-8"))
                        
                        # self.conts.append(command)
                        # print("CONNECTION")
                        if command["command"] == "create":
                            # print("CREATE RECEIVED")
                            name = command["cont"]["name"]
                            setts = command["cont"]["settings"]
                            self.conts[name] = setts
                            pass
                        elif command["command"] == "destroy":
                            del self.conts[command["name"]]
                            pass
                        elif command["command"] == "start":
                            self.conts[command["name"]]["status"] = "running"
                            pass
                        elif command["command"] == "stop":
                            self.conts[command["name"]]["status"] = "idle"
                            pass
                        elif command["command"] == "freeze":
                            self.conts[command["name"]]["status"] = "frozen"
                        elif command["command"] == "unfreeze":
                            if self.conts[command["name"]]["status"] == "frozen":
                                self.conts[command["name"]]["status"] = "running"
                            elif self.conts[command["name"]]["status"] == "idle":
                                pass
                        elif command["command"] == "status":
                            if command["name"] in self.conts:
                                conn.sendall(json.dumps(self.conts[command["name"]]).encode("utf-8"))
                            else:
                                conn.sendall(b"Container doesn't exist")
                        # with open("/home/jthiede/Desktop/GitRepos/lxd-carbon/output.log", "w") as f:
                            
                        #     f.write(str(string))
            pass

        except Exception as ex:

            with open(config.WORKING_DIR + "/listen_excep.log", "w") as f:
                f.write(str(ex))

    def check_carbon(self):
        try:
            while True:
                # print(containers)
                time.sleep(config.UPDATE_PERIOD)

                carbon = config.getCarbonIntensity()

                f = open(config.WORKING_DIR +  "/test.log", "w") 
                f.write(str(self.conts))
                f.close()

                for contName in self.conts:
                    with open(config.WORKING_DIR + "/loop.test", "w") as f:
                        f.write(str(contName))
                    self.applyPolicy(contName, self.conts[contName], carbon)

                # for cont in self.conts:
                #   f = open("/home/jthiede/Desktop/GitRepos/lxd-carbon/" + str(cont) + ".log", "w") 
                #f = open("/users/jthiede/test.log", "w") 
                #f.write(str(self.conts))
                #f.close()
        
        except Exception as ex:

            with open(config.WORKING_DIR + "/checkcarbon_excep.log", "w") as f:
                f.write(str(ex))

    def applyPolicy(self, contName, contSetts, carb):
        try:
            with open(config.WORKING_DIR + "/function.test", "w") as f:
                f.write("Hello")
            if contSetts["status"] == "idle":
                return

            elif contSetts["status"]== "frozen" and carb < int(contSetts["threshold"]):
                # Resume operation
                command = ["lxc-unfreeze", "-n", str(contName)]
                
                subprocess.Popen(command).communicate()
                contSetts["status"] = "running"
                pass

            if contSetts["policy"] == "wait":
                if carb > int(contSetts["threshold"]):
                    
                    # Suspend container
                    command = ["lxc-freeze", "-n", str(contName)]
                    
                    subprocess.Popen(command).communicate()
                    contSetts["status"] = "frozen"
                    pass
                
            if contSetts["policy"] == migrate:
                if carb > contSetts["threshold"]:
                    pass
                    target = self.migrate_target(True)

                    if target == "none":
                        return
                    
                    self.migrate_send(contName=contName, target=target)
                
                elif carb < contSetts["threshold"]*config.SCALEUP_THRESH:
                    target = self.migrate_target(False)

                    if target == "none":
                        return
                    
                    self.migrate_send(contName=contName, target=target)
        
        except Exception as ex:
            with open(config.WORKING_DIR + "/excep.log", "w") as f:
                f.write(str(ex))
    

    def getAllPids(self):

        try:
            pass
            psCmd = ['ps', '-e', '-o', 'pid']
            out = subprocess.Popen(psCmd, stdout=subprocess.PIPE).communicate()[0]
            out = ''.join(map(chr,out))

            return out.split()[1:]
        except Exception as ex:
                    
            with open(config.WORKING_DIR + "/getpid_excep.log", "w") as f:
                f.write(str(ex))
    

    def getPerfEvents(self, pids):
        try:
            q = Queue()
            procs = []
            for pid in pids:
                p = Process(target=self.perfStat, args=(pid,q))
                procs.append(p)
                # print("Launcing proc check " + str(pid))
                p.start()
            # print(len(procs))
            for proc in procs:
                # print("Waiting on " + str(proc))
                proc.join()
                # print("Joined")


            # print("DONE")
            containers = {}
            for i in range(len(pids)):
                #print("ITER " + str(i))
                pid, counters = q.get()
                for e in counters:
                    #print(e)
                    if counters[e] == "<not counted>":
                        counters[e] = 0.0
                    else:
                        counters[e] = float(counters[e])
                # print("q.get done")
                cont = pids[pid]
                # count = Counter()
                # print("SUM")
                if cont in containers:
                    newSums = [i+j for i,j in zip(list(counters.values()),list(containers[cont].values()))]
                    newCount = dict(zip(events, newSums))
                    containers[cont] = newCount
                else:
                    containers[cont] = counters
            pass
            # print(containers)
            return containers
        except Exception as ex:

            with open(config.WORKING_DIR + "/perfevents_excep.log", "w") as f:
                f.write(str(ex))

    def perfStat(self,pid,q):
        pass
        try:
            with open(config.WORKING_DIR + "/perfstat.test", "w") as f:
                f.write("Hello")

            events = ["task-clock", "context-switches", "cpu-migrations", "page-faults", "cycles", "instructions", "branches", "branch-misses"]
            cmd = ["perf", "stat", "-p", str(pid), "-x", ",", "sleep", "5"]
            out = subprocess.Popen(cmd, stderr=subprocess.PIPE).communicate()[1]
        

            lines = [l.replace("b'", "").split(",")[0] for l in str(out).split("\\n") if l != "'" ]
            d = dict(zip(events, lines))
            
            with open(config.WORKING_DIR + "/procOut/"+str(pid)+"Out.log", 'w') as f:
                f.write(str(lines))
            q.put((pid,d))
       
        except Exception as ex:

            with open(config.WORKING_DIR + "/perfstat_excep.log", "w") as f:
                f.write(str(ex))

    def powerEstimate(self, conts):
        try:
            with open(config.MODEL, 'rb') as f:
                model = pickle.load(f)

            carbon = config.getCarbonIntensity()

            for cont in conts:
                feats = list(conts[cont].values())
                feats = [feats]
                # print(feats)
                pred = float(model.predict(feats))
                # print(pred)

                power = pred - config.BASE_POW

                self.conts[cont]["totals"]["joules_total"] += power * config.UPDATE_PERIOD
                
                self.conts[cont]["totals"]["carbon_total"] += carbon * power * config.UPDATE_PERIOD
                pass

        except Exception as ex:
            with open(config.WORKING_DIR + "/model_excep.log", "w") as f:
                f.write(str(ex))

    def procMonitor(self):
        try:
            while True:
                 
                time.sleep(config.UPDATE_PERIOD)

                with open(config.WORKING_DIR + "/monitor.test", "w") as f:
                    f.write("Hello")
                pids = self.getAllPids()
                groupMap = {}
                for pid in pids:
                    cat = ["cat", "/proc/"+str(pid)+"/cgroup" ]
                    systemd = ["systemctl"]
                    catOut = str(subprocess.Popen(cat, stdout=subprocess.PIPE).communicate()[0])
                    try:
                        group = re.findall(r"lxc/([\w-]+)", str(catOut))[0]
                    except Exception as e:
                        continue
            

                    groupMap[pid] = group

                if os.path.exists(config.WORKING_DIR + "/procOut"):
                    rm = ["rm", "-r", config.WORKING_DIR + "/procOut"]
                    subprocess.Popen(rm).communicate()
                os.mkdir(config.WORKING_DIR + "/procOut")   
                #print(groupMap)
                # print(groupMap)
                conts = self.getPerfEvents(groupMap)

                with open(config.WORKING_DIR + "/procMonitor.out", "w") as f:
                    f.write(str(conts))

                self.powerEstimate(conts)
        except Exception as ex:
            with open(config.WORKING_DIR + "/procMonitor_excep.log", "w") as f:
                f.write(str(ex))


    def migrate_target(self, scale_down):

        cur_cpu = 0
        cur_mem = 0
        for m in config.MIGRATION_MACHINES:
            if m["host"]  == self.host:
                cur_cpu = m["cpu"]
                cur_mem = m["memGB"]
    
            
            
        for m in config.MIGRATION_MACHINES:
            if m["host"] in self.host:
                continue
            else:
                if scale_down and m["cpu"] < cur_cpu  :
                    return m["host"]
            
                if not(scale_down) and m["cpu"] > cur_cpu:
                    return m["host"]
        
        return "none"
        pass

    # Migration Policy: Send to target machine
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
        zipCont = ["zip", "-r", str(contName)+".zip", str(contName)]
        subprocess.Popen(zipCont).communicate()
    
        
        print("scp filesystem")
        scp = ["scp", str(contName) + ".zip", config.SSH_USER+"@"+target+":/var/lib/lxc"]
        subprocess.Popen(scp).communicate()
        
        os.chdir(config.WORKING_DIR)

        print("destroy old")
        destroyOldCont = ["lxc-destroy", str(contName)]
        subprocess.Popen(destroyOldCont).communicate()
        rm1 = ["rm", "-r", str(contName)]
        rm2 = ["rm", str(contName)+".zip"]
        subprocess.Popen(rm1).communicate()
        subprocess.Popen(rm2).communicate()

        # self.conts[contName]["status"] = "remote @ " + str(target)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect( (target, config.MIGRATION_PORT) )
            encode = json.dumps({contName: self.conts[contName]}).encode("utf-8")
            s.sendall(encode)


        pass


    # def migrate_recv(self):
    #     while True:
    #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        
    #             s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #             s.bind( (self.host, config.MIGRATION_PORT) )
    #             s.listen(1)
    #             conn, addr = s.accept()

    #             with conn:
    #                 data = conn.recv(2048)
    #                 cont = json.loads(data.decode("utf-8"))

    #                 name = list(cont.keys())[0]


    #                 untar = ["tar", "--numeric-owner", "-cvf", "/var/lib/lxc/"+str(name)+".tar", "/var/lib/lxc"]
    #                 subprocess.Popen(untar).communicate()

    #                 restart = ["lxc-checkpoint", "-r", "-D", "/var/lib/lxc/"+str(name)+"/checkpoint_"+str(name)]
    #                 subprocess.Popen(restart).communicate()
    #                 # self.conts[cont[""]]

    def migrate_recv(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind( (self.host, config.MIGRATION_PORT) )
                # print("listening")
                s.listen(1)
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(2048)
                    cont = json.loads(data.decode("utf-8"))

                    name = list(cont.keys())[0]

                    # print("unzip")
                    unzip = ["unzip", "/var/lib/lxc/"+str(name)+".zip"]
                    subprocess.Popen(unzip).communicate()

                    # print("relocate")
                    move = ["mv", str(name), "/var/lib/lxc"]
                    subprocess.Popen(move).communicate()

                    # print("restore")
                    restart = ["lxc-checkpoint", "-r", "-D", "/var/lib/lxc/"+str(name)+"/check", "-n", str(name)]
                    subprocess.Popen(restart).communicate()
                    # self.conts[cont[""]]

                    # print("cleanup")
                    cleanup1 = ["rm", "/var/lib/lxc/"+str(name)+".zip"]
                    cleanup2 = ["rm", "-r", "/var/lib/lxc/"+str(name)+"/check"]

                    subprocess.Popen(cleanup1).communicate()
                    subprocess.Popen(cleanup2).communicate()

                    self.conts[name] = cont[name]

# # t1 = threading.Timer(1.0, check_carbon)
# t2 = threading.Timer(1.0, listen)

# # t1.start()
# t2.start()


# def main(self):
#     # t1 = threading.Timer(1.0, check_carbon)
#     t2 = threading.Timer(1.0, listen)

#     # t1.start()
#     t2.start()


if __name__ == "__main__":
    
    d = LXC_C_Daemon(config.WORKING_DIR + "/daemon.pid")

    if sys.argv[1] == "start":
        d.start()
    
    elif sys.argv[1] == "stop":
        d.stop()

    sys.exit(0)

# import Pyro4

# @Pyro4.expose
# @Pyro4.behavior(instance_mode="single")
# class LXCCarbon(object):
    
#     def __init__(self):

#         self.containers = {}
    
#     def register(self, name, policy, quota):
#         self.containers[name] = {policy, quota}

#     def list(self):
#         for cont in self.containers:
#             print(self.containers[cont])



# def main():
#     Pyro4.Daemon.serveSimple(
#         {
#             LXCCarbon: "lxc-c"
#         },
#         ns=False
#     )


# if __name__ == "__main__":
#     main()

# Pyro4.core.initServer()
# daemon = Pyro4.core.Daemon()
# uri = daemon.connect(LXCCarbon(), "lxc-c")

# print("Daemon runnin on port: " + str(daemon.port))
# print("Pyro URI = " + str(uri))

# daemon.requestLoop()
