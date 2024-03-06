from gpiozero import Button, LED, Device
from gpiozero.pins.lgpio import LGPIOFactory as fact
#from gpiozero.pins.pigpio import PiGPIOFactory as fact
from signal import pause

Device.pin_factory = fact()



def say_hello():
    print("Hello")

button1 = Button(17, pull_up = True, bounce_time=0.3)
button2 = Button(27, pull_up=True, bounce_time=0.3)
led_red = LED(24)
led_green = LED(23)
led_red.on()
led_green.on()

button1.when_pressed = say_hello
button1.when_released = led_red.toggle

button2.when_pressed = led_green.toggle

pause()
