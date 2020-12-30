import time
import json
import requests
from pymodbus.client.sync import ModbusTcpClient
import sys

MODBUSPORT = 502
v_scale = 100.0 * (2**-15)
i_scale = 100.0 * (2**-15)
p_scale = 6500.0 * (2**-15)
if len(sys.argv) == 5:
    PORT = sys.argv[4]
else:
    PORT = 80
teleceptorURL = "http://localhost:" + str(PORT) + "/api/station/"


def getData(IP):
    client = ModbusTcpClient(IP, port=MODBUSPORT)
    client.connect()
    result = client.read_holding_registers(0x00, 35, unit=1)
    i = 1
    reg = {}
    for r in result.registers:
        reg[i] = int(r)
        i = i + 1
    client.close()


    return [
        {'name': 'arrayvoltage', 'description': 'Array Voltage', 'units': 'V', 'value': reg[2], 'scale': v_scale},
        {'name': 'sweepvmp', 'description': 'Sweep Vmp', 'units': 'V', 'value': reg[33], 'scale': v_scale},
        {'name': 'sweepvoc', 'description': 'Sweep Voc', 'units': 'V', 'value': reg[35], 'scale': v_scale},
        {'name': 'sweeppmax', 'description': 'Sweep Pmax', 'units': 'W', 'value': reg[34], 'scale': p_scale},
        {'name': 'battvoltage', 'description': 'Battery Voltage', 'units': 'V', 'value': reg[1], 'scale': v_scale},
        {'name': 'chargecurrent', 'description': 'Charge Current', 'units': 'A', 'value': reg[4], 'scale': i_scale},
        {'name': 'loadstate', 'description': 'Load State', 'units': '', 'value': reg[19], 'scale': 1},
        {'name': 'loadvoltage', 'description': 'Load Voltage', 'units': 'V', 'value': reg[3], 'scale': v_scale},
        {'name': 'loadcurrent', 'description': 'Load Current', 'units': 'A', 'value': reg[5], 'scale': i_scale},
        {'name': 'ambienttemp', 'description': 'Ambient Temp', 'units': 'C', 'value': reg[8], 'scale': 1},
        {'name': 'batterytemp', 'description': 'Battery Temp', 'units': 'C', 'value': reg[7], 'scale': 1},
        {'name': 'heatsinktemp', 'description': 'Heat Sink Temp', 'units': 'C', 'value': reg[6], 'scale': 1}
    ]


def poll(data, IP, name, model):
    motestring = {"info": {"uuid": name, "name": name, "description": "", "in": [], "out": []}}
    readings = {'readings': []}
    for d in data:
        motestring['info']['out'].append({"units": d['units']})
        motestring['info']['out'][-1]["model"] = model
        motestring['info']['out'][-1]["name"] = d['name']
        motestring['info']['out'][-1]["description"] = d['description']
        motestring['info']['out'][-1]["scale"] = [d['scale'], 0]
        motestring['info']['out'][-1]["timestamp"] = time.time()
        motestring['info']['out'][-1]["sensor_type"] = "int"
        readings['readings'].append([d['name'], d['value'], time.time()])
    postmessage = [{'info': motestring['info'], 'readings': readings['readings']}]

    for sensor in postmessage[0]['info']['out']:
        sensor.update({'meta_data': {'unixtime': time.time(), 'ipaddress': IP, 'port': str(MODBUSPORT)}})
    response = requests.post(teleceptorURL, data=json.dumps(postmessage))


def main():
    data = getData(sys.argv[1])
    poll(data, sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print 'Usage: ', sys.argv[0], ' <ip> <uuid> <device model> <optional teleceptor port. default:80>'
        sys.exit()

    main()
