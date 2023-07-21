'''
CONFIG FILE FOR CARBON CONTAINERS
'''



MIGRATION_MACHINES = {  "155.98.38.48": {"host": "155.98.38.48", "cpu": 8, "memGB": 12, "basepow":25000 },
                        "155.98.36.98": {"host": "155.98.36.98", "cpu": 32, "memGB": 63, "basepow": 100000 },
                        "155.98.39.98": {"host": "155.98.39.98", "cpu": 2, "memGB": 2, "basepow": 6250 }}



CO2_SIGNAL_KEY = "/users/jthiede/co2key.txt"

'''
FRONT END VALUES
'''

FRONT_IP = "localhost"
FRONT_PORT = "1994"


'''
RECORDS VALUES

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
CONTROLLER VALUES
'''

CONTROLLER_PORT = "1997"
SSH_KEY_PATH = "/users/jthiede/id_rsa"
SSH_USER = "jthiede"
MIGRATION_PORT = 8888


'''
CARBON POLICY VALUES
'''

UPDATE_PERIOD = 300
SCALEUP_THRESH = 0.5


'''
LXC-C DAEMON VALUES
'''


HOST = "localhost"
PORT = 1994

WORKING_DIR = "./"

OUTPUT = "/users/jthiede/eff/carbon"
M_OUTPUT = "/users/jthiede/eff/migrations"


'''
CARBON DATA FUNCTION: REPLACE WITH YOUR IMPLEMENTATION

    Ensure input signature remains with NO PARAMETERS

    Ensure output is an INT representing CARBON INTENSITY in units: (Grams CO2 / kilowatt*hour)
'''

first_5_hours = [300.91, 307.31, 307.78, 313.35, 317.95]
def getCarbonIntensity():
    return first_5_hours[0]

# Different funcs for different APIs
# in: api key
# out: Co2/Wh or Ws

# Electricity Map et al

# Integrate with below as primary
# https://www.co2signal.com/

# import subprocess
# import json
# def getCarbonIntensity():

#     def mws_to_kwh(n):
#         return n / (3600000000)
#         pass
    
#     with open(CO2_SIGNAL_KEY, "r") as f:
#         token = f.read().strip()
    
#     #curl 'https://api.co2signal.com/v1/latest?countryCode=DK-DK1' -H 'auth-token: ....'
#     curl = ["curl", "https://api.co2signal.com/v1/latest?countryCode=US", "-H", "auth-token:" + str(token)]
#     out = subprocess.Popen(curl, stdout=subprocess.PIPE).communicate()[0]

#     out = json.loads(str(out.decode("utf-8")))

#     return int(out["data"]["carbonIntensity"])
#     pass
