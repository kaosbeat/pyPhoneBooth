import os, io

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

if __name__ == "__main__":
    if is_raspberrypi():
        print("this script gets executed on a pi")
    else:
        print("not a pi this is")
