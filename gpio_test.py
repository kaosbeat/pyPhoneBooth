import time

from detect_pi import is_raspberrypi
import RPi.GPIO as GPIO


# Define GPIO pins
class gpio_class:
    def __init__(self):
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

        # Set up button event detection
        GPIO.add_event_detect(self.GPIO_BUTTON_1, GPIO.BOTH, callback=self.notify_gpio, bouncetime=300)
        GPIO.add_event_detect(self.GPIO_BUTTON_2, GPIO.BOTH, callback=self.notify_gpio, bouncetime=300)

    def notify_gpio(self, channel):
        print("reading from {} saying {}".format(channel, GPIO.input(channel)))


if __name__ == '__main__':
    gpio = gpio_class()
    while True:
        time.sleep(0.1)
