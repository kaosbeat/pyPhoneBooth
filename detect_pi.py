import io


def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception:
        pass
    return False

def raspberrypi_version():
    try:
        with io.open('/proc/device-tree/compatible', 'r') as m:
            x = m.read().lower()
            if '5' in x:
                  return 5
            if '4' in x:
                  return 4
            if '3' in x:
                  return 3
            if 'zero' in x:
                  return 0
            else:
                  print("not sure which rpi board you've got there mate")
                  return _
    except Exception as e:
        print("exception reading rpi version: {}".format(e))
    return False

if __name__ == "__main__":
    if is_raspberrypi():
        print("this script gets executed on a pi {}".format(raspberrypi_version()))
    else:
        print("not a pi this is")

    
