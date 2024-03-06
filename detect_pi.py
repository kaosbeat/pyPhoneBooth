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
            match m:
                case "raspberrypi,5-model-bbrcm,bcm2712":
                    return 5
                case "raspberrypi,4-model-bbrcm,bcm2711":
                    return 4
                case "raspberrypi,model-zero-wbrcm,bcm2835":
                    return 0
                case _:
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

    
