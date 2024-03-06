import time

from detect_pi import is_raspberrypi
import RPi.GPIO as GPIO
import atexit


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
    def __init__(self, callback_function=None):


        self.GPIO_BUTTON_1 = 17
        self.GPIO_BUTTON_2 = 27
        self.GPIO_RED_LED = 24
        self.GPIO_GREEN_LED = 23

        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.GPIO_BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.GPIO_RED_LED, GPIO.OUT)
        GPIO.setup(self.GPIO_GREEN_LED, GPIO.OUT)

        self.callback = callback_function if callback_function is not None else notify_gpio

        # Set up button event detection
        GPIO.add_event_detect(self.GPIO_BUTTON_1, GPIO.BOTH, callback=self.callback, bouncetime=600)
        GPIO.add_event_detect(self.GPIO_BUTTON_2, GPIO.BOTH, callback=self.callback, bouncetime=300)

        atexit.register(self.exit_handler)

    def exit_handler(self):
        print("cleaning GPIOs")
        GPIO.cleanup()

    def switch_led(self, to_green: bool):
        if to_green:
            GPIO.output(self.GPIO_RED_LED, GPIO.HIGH)
            GPIO.output(self.GPIO_GREEN_LED, GPIO.LOW)
        else:
            GPIO.output(self.GPIO_RED_LED, GPIO.LOW)
            GPIO.output(self.GPIO_GREEN_LED, GPIO.HIGH)


def test_callback_function(channel):
    print(channel)


if __name__ == '__main__':
    gpio = gpio_class()
    # gpio = gpio_class(test_callback_function)
    print("starting GPIO test on GPIOs 17 & 27")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\r\nexiting\r\n")
