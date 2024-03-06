from gpiozero import Button, LED, Device
from gpiozero.pins.lgpio import LGPIOFactory as fact
#from gpiozero.pins.pigpio import PiGPIOFactory as fact
from signal import pause
import time

Device.pin_factory = fact()

def test():
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

# Define GPIO pins
def notify_gpio(channel):
    first_reading = GPIO.input(channel)
    time.sleep(0.1)
    second_reading = GPIO.input(channel)
    if first_reading == second_reading:
        print("got a {} from channel {}".format(first_reading, channel))
    else:
        print("first got a {}, then a {} from channel {}".format(first_reading, second_reading, channel))


class gpio_class:
    def __init__(self, callback_function_pressed=None, callback_function_released = None):
        self.GPIO_BUTTON_1 = 17
        self.GPIO_BUTTON_2 = 27
        self.GPIO_RED_LED = 24
        self.GPIO_GREEN_LED = 23
        self.button1 = Button(self.GPIO_BUTTON_1, pull_up = True, bounce_time=0.3)
        self.button2 = Button(self.GPIO_BUTTON_2, pull_up=True, bounce_time=0.3)
        self.led_red = LED(self.GPIO_RED_LED)
        self.led_green = LED(self.GPIO_GREEN_LED)
        
        self.button1.when_pressed = callback_function_pressed if callback_function_pressed is not None else notify_gpio
        self.button1.when_released = callback_function_released if callback_function_released is not None else notify_gpio
        
        self.button2.when_pressed = callback_function_pressed if callback_function_pressed is not None else notify_gpio
        self.button2.when_released = callback_function_released if callback_function_released is not None else notify_gpio
        
    def switch_led(self, to_green: bool):
        if to_green:
           self.led_green.on()
           self.led_red.off()
        else:
            self.led_green.off()
            self.led_red.off()
            
if __name__ == '__main__':
    gpio = gpio_class()
    # gpio = gpio_class(test_callback_function)
    print("starting GPIO test on GPIOs 17 & 27")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\r\nexiting\r\n")