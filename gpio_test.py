from detect_pi import is_raspberrypi
import RPi.GPIO as GPIO
# Define GPIO pins
class gpio_class:
    def __init__(self):
            self.GPIO_BUTTON = 27
            self.GPIO_RED_LED = 24
            self.GPIO_GREEN_LED = 23

            # Set up GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.GPIO_RED_LED, GPIO.OUT)
            GPIO.setup(self.GPIO_GREEN_LED, GPIO.OUT)

            # Set up button event detection
            GPIO.add_event_detect(self.GPIO_BUTTON, GPIO.BOTH, callback=self.notify_gpio, bouncetime=300)

    def notify_gpio(self, channel):
        print(channel)
        print(GPIO.input(self.GPIO_BUTTON))