'''
CONFIG FILE FOR LXC-C
'''


CO2_SIGNAL_KEY = ""


'''
LXC-C MONITOR VALUES
'''

MODEL = "./model.pkl"
BASE_POW = 100000


'''
LXC-C DAEMON VALUES
'''
WORKING_DIR = "/home/jpthiede"
LOCKFILE = ""

HOST = "localhost"
PORT = 1994


UPDATE_PERIOD = 30

# Different funcs for different APIs
# in: api key
# out: Co2/Wh or Ws

# Electricity Map et al

# Integrate with below as primary
# https://www.co2signal.com/
def getCarbonIntensity():
    return 0
    pass