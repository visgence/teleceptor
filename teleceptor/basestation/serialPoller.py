"""
Authors: Cyrille Gindreau (Visgence, Inc.).

Takes a device name as argument and passes it to GenericQueryer
"""
from teleceptor.basestation import GenericQueryer


if __name__ == "__main__":
    name = ""
    for k, v in globals().items():
        if 'DEVICENAME' is k:
            name = v[0]
    GenericQueryer.main(60, deviceName=name, timeout=360, debug=False)
