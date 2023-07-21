import sys
import time
import csv
import subprocess

CPU = [64.12153865,
65.17606178,
85.88995132,
22.16390897,
16.84730746,
33.22625081,
33.8283746,
32.19938291,
30.97829546,
74.02062032,
64.53220577,
72.79312028,
65.51646486,
34.46565519,
31.81011653,
31.15854799,
33.41623525,
31.30939486,
32.2838608,
31.84333595,
31.43453764,
13.0064163]

for i in range(len(CPU)):
    print(i)
    stress = ["timeout",  "30",  "stress-ng", "--cpu", "8", "--cpu-load",  str(CPU[i])+"%"]
    subprocess.Popen(stress).communicate()
