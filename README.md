# Carbon Containers

### Setup

To run this you should have LXC, CRIU, and the perf tool from linux-tools-common installed:

```
apt-get install lxc
apt-get install criu
apt-get install linux-tools-common
```

This implementation uses Python 3.7+, and the following python packages:

```
grcpio
grpcio-tools
scikit-learn
```


Lastly, we suggest you use CO2Signal/ElectricityMap for carbon data: https://www.co2signal.com/

(The carbon data source can be freely changed by modifying the function in code/v2/config.py)



