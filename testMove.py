import sys
import os
import config
import subprocess
import socket
import json

def migrate_target(scale_down, curHost):

    cur_cpu = 0
    cur_mem = 0
    for m in config.MIGRATION_MACHINES:
        if m["host"] == curHost:
            cur_cpu = m["cpu"]
            cur_mem = m["memGB"]

        
        
    for m in config.MIGRATION_MACHINES:
        if m["host"]  == curHost:
            continue
        else:
            if scale_down and m["cpu"] < cur_cpu  :
                print("Select target: " + str(m["host"]))
                return m["host"]
        
            if not(scale_down) and m["cpu"] > cur_cpu:
                return m["host"]
    
    return "none"
    pass

# Migration Policy: Send to target machine
def migrate_send(contName, target, cont):

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
        encode = json.dumps(cont).encode("utf-8")
        s.sendall(encode)


    pass


def migrate_recv(host):
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind( (host, config.MIGRATION_PORT) )
            print("listening")
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                data = conn.recv(2048)
                cont = json.loads(data.decode("utf-8"))

                name = list(cont.keys())[0]

                print("unzip")
                unzip = ["unzip", "/var/lib/lxc/"+str(name)+".zip"]
                subprocess.Popen(unzip).communicate()

                print("relocate")
                move = ["mv", str(name), "/var/lib/lxc"]
                subprocess.Popen(move).communicate()

                print("restore")
                restart = ["lxc-checkpoint", "-r", "-D", "/var/lib/lxc/"+str(name)+"/check", "-n", str(name)]
                subprocess.Popen(restart).communicate()
                # self.conts[cont[""]]

                print("cleanup")
                cleanup1 = ["rm", "/var/lib/lxc/"+str(name)+".zip"]
                cleanup2 = ["rm", "-r", "/var/lib/lxc/"+str(name)+"/check"]

                subprocess.Popen(cleanup1).communicate()
                subprocess.Popen(cleanup2).communicate()

if __name__ == "__main__":
    cont = {"c1": {"threshold": 200, "policy": "migrate", "status": "idle",  "totals": {"carbon_total": 0, "joules_total": 0}} }
    if sys.argv[1] == "send":
        target = migrate_target(True, "198.22.255.21", cont)
        

        migrate_send(cont["name"], target=target)
        pass
    elif sys.argv[1] == "recv":
        migrate_recv("198.22.255.33")
    pass
