'''
CONFIG FILE FOR LXC-C
'''


CO2_SIGNAL_KEY = "co2key.txt"


'''
LXC-C MONITOR VALUES
'''

MODEL = "./model.pkl"
BASE_POW = 100000


'''
LXC-C DAEMON VALUES
'''
WORKING_DIR = "/users/jthiede"
LOCKFILE = ""

HOST = "localhost"
PORT = 1994


UPDATE_PERIOD = 30

SSH_KEY_PATH = "./"
SSH_USER = ""

MIGRATION_MACHINES = {}
# MIGRATION_MACHINES = [{"host": "198.22.255.21", "cpu": 40, "memGB": 252 }, {"host": "198.22.255.33", "cpu": 20, "memGB": 150 }]

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