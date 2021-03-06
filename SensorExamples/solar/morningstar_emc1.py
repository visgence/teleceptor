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


def ScaleF16(val):
        currentVal = (val & 0x03ff) / 1024.0
        val >>= 10
        e = (val & 0x001f)
        val >>= 5
        s = val & 0x0001
        if (e == 0):
            if (currentVal == 0):
                return(0)
            currentVal *= (2.0 ** -14)
            if (s != 0):
                currentVal *= -1.0
            return (currentVal)
        if (e == 0x1f):
            if (currentVal == 0):
                if (s == 0):
                    return(float('inf'))
                else:
                    return (float('-inf'))
            else:
                return(0 / 0)
        currentVal += 1.0
        currentVal *= (2.0 ** (e - 15))
        if (s != 0):
            currentVal *= -1.0
        return (currentVal)


def getData(IP):
    client = ModbusTcpClient(IP, port=MODBUSPORT)
    client.connect()
    if sys.argv[3] == "ProstarMPPT":
        result = client.read_holding_registers(0x08, 65, unit=1)
    else:
        result = client.read_holding_registers(0x08, 35, unit=1)
    i = 1
    reg = {}
    for r in result.registers:
        reg[i] = int(r)
        i = i + 1
    client.close()
    if sys.argv[3] == "ProstarMPPT":
        ambienttemp = ScaleF16(reg[29])
        batterytemp = ScaleF16(reg[28])
        heatsinktemp = ScaleF16(reg[27])
        # http://support.morningstarcorp.com/wp-content/uploads/2015/12/PSMPPT_public-MODBUS-doc_v04.pdf
        # PDU Addr  Logical Addr Variable name   Variable description                        Units Scaling or Range
        # 0x0013    20           adc_va_f_shadow Array Voltage                               V     Float16
        # 0x003D    62           Sweep_Vmp       Array Vmp (found during sweep)              V     Float16
        # 0x003F    64           Sweep_Voc       Array Voc (found during sweep)              V     Float16
        # 0x003E    63           Sweep_Pmax      Array Max Output Power (found during sweep) W     Float16
        # 0x0012    19           adc_vbterm      Battery Terminal Voltage                    V     Float16
        # 0x0010    17           adc_ic_f_shadow Charge Current                              A     Float16
        # 0x002E    47           load_state      Load State
        # 0x0014    21           adc_vl          Load Voltage                                V     Float16
        # 0x0016    23           adc_il          Load Current                                A     Float16
        # 0x001C    29           T_amb           Ambient (local) Temperature                 C     Float16
        # 0x001B    28           T_batt          Battery Temperature (Either Ambient or RTS) C     Float16
        # 0x001A    27           T_hs            Heatsink Temperature                        C     Float16
        # 0x0021    34           charge_state    Charge State
        # 0x002B    44           kWhc_t          Kwh Charge Total                            kWh   n*0.1
        # 0x0028    41           Ahc_t_HI        Ah Charge Total, HI word                    Ah    n*0.1
        # 0x0040    65           va_ref          Array Target Voltage                        V     Float16
        # 0x0034    53           Ahl_t_HI        Ah Load Total, HI word                      Ah    n*0.1
        return [
            {'name': 'arrayvoltage', 'description': 'Array Voltage', 'units': 'V', 'value': reg[20], 'scale': v_scale},
            {'name': 'sweepvmp', 'description': 'Sweep Vmp', 'units': 'V', 'value': reg[62], 'scale': v_scale},
            {'name': 'sweepvoc', 'description': 'Sweep Voc', 'units': 'V', 'value': reg[64], 'scale': v_scale},
            {'name': 'sweeppmax', 'description': 'Sweep Pmax', 'units': 'W', 'value': reg[63], 'scale': p_scale},
            {'name': 'battvoltage', 'description': 'Battery Voltage', 'units': 'V', 'value': reg[19], 'scale': v_scale},
            {'name': 'chargecurrent', 'description': 'Charge Current', 'units': 'A', 'value': reg[17], 'scale': i_scale},
            {'name': 'loadstate', 'description': 'Load State', 'units': '', 'value': reg[47], 'scale': 1},
            {'name': 'loadvoltage', 'description': 'Load Voltage', 'units': 'V', 'value': reg[21], 'scale': v_scale},
            {'name': 'loadcurrent', 'description': 'Load Current', 'units': 'A', 'value': reg[23], 'scale': i_scale},
            {'name': 'ambienttemp', 'description': 'Ambient Temp', 'units': 'C', 'value': ambienttemp, 'scale': 1},
            {'name': 'batterytemp', 'description': 'Battery Temp', 'units': 'C', 'value': batterytemp, 'scale': 1},
            {'name': 'heatsinktemp', 'description': 'Heat Sink Temp', 'units': 'C', 'value': heatsinktemp, 'scale': 1},
            {'name': 'chargestate', 'description': 'Charge State', 'units': '', 'value': reg[34], 'scale': 1},
            {'name': 'kwhcharge', 'description': 'Kwh Charge Total', 'units': 'kWh', 'value': reg[44], 'scale': 0.1},
            {'name': 'ahcharge', 'description': 'Ah Charge Total, HI word', 'units': 'Ah', 'value': reg[41], 'scale': 0.1},
            {'name': 'arraytargetvoltage', 'description': 'Array Target Voltage', 'units': 'V', 'value': reg[65], 'scale': v_scale},
            {'name': 'ahload', 'description': 'Ah Load Total, HI word', 'units': 'Ah', 'value': reg[53], 'scale': 0.1}
        ]
    else:
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
#    print(time.time())
    poll(data, sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print 'Usage: ', sys.argv[0], ' <ip> <uuid> <device model> <optional teleceptor port. default:80>'
        sys.exit()

    main()
