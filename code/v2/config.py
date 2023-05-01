'''
CONFIG FILE FOR LXC-C
'''


CO2_SIGNAL_KEY = "/users/jthiede/co2key.txt"

'''
FRONT END VALS
'''

FRONT_IP = "localhost"
FRONT_PORT = "1994"


'''
RECORDS

'''
RECORD_IP = "localhost"
RECORD_PORT = "1996"
RECORD_FILE = "./conts.json"

'''
MONITOR VALUES
'''

IP = "localhost"
PORT = "1995"

MODEL = "/users/jthiede/model.pkl"
MODEL_BASE_POW = 100000


'''
CONTROLLER
'''

CONTROLLER_PORT = "1997"

'''
LXC-C DAEMON VALUES
'''
WORKING_DIR = "/users/jthiede"
# WORKING_DIR = "./"
LOCKFILE = ""

HOST = "localhost"
PORT = 1994


UPDATE_PERIOD = 30

SSH_KEY_PATH = "/users/jthiede/id_rsa"
SSH_USER = "jthiede"

# MIGRATION_MACHINES = {}
MIGRATION_MACHINES = {  "198.22.255.16": {"host": "198.22.255.16", "cpu": 2, "memGB": 252, "basepow":100000 },
                        "198.22.255.78": {"host": "198.22.255.78", "cpu": 4, "memGB": 126, "basepow": 50000 }}

MIGRATION_PORT = 8888

SCALEUP_THRESH = .5

# Different funcs for different APIs
# in: api key
# out: Co2/Wh or Ws

# Electricity Map et al

# Integrate with below as primary
# https://www.co2signal.com/
import subprocess
import json
def getCarbonIntensity():

    def mws_to_kwh(n):
        return n / (3600000000)
        pass
    
    with open(CO2_SIGNAL_KEY, "r") as f:
        token = f.read().strip()
    
    #curl 'https://api.co2signal.com/v1/latest?countryCode=DK-DK1' -H 'auth-token: ....'
    curl = ["curl", "https://api.co2signal.com/v1/latest?countryCode=US", "-H", "auth-token:" + str(token)]
    out = subprocess.Popen(curl, stdout=subprocess.PIPE).communicate()[0]
    # print(str(out))
    # print(type(out))
    out = json.loads(str(out.decode("utf-8")))
    # print(out["data"])
    return int(out["data"]["carbonIntensity"])
    pass
