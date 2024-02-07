import RPi.GPIO as GPIO
import time

# Define GPIO pins
GPIO_BUTTON = 27
GPIO_GREEN_LED = 23
GPIO_RED_LED = 24

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_GREEN_LED, GPIO.OUT)
GPIO.setup(GPIO_RED_LED, GPIO.OUT)

# Define callback function
def callback_function(channel):
    if GPIO.input(GPIO_BUTTON):  # Button is not pressed
        print("Button released, turning on red LED")
        GPIO.output(GPIO_GREEN_LED, GPIO.LOW)
        GPIO.output(GPIO_RED_LED, GPIO.HIGH)
    else:  # Button is pressed
        print("Button pressed, turning on green LED")
        GPIO.output(GPIO_GREEN_LED, GPIO.HIGH)
        GPIO.output(GPIO_RED_LED, GPIO.LOW)
# Add event detection to the button GPIO pin
GPIO.add_event_detect(GPIO_BUTTON, GPIO.BOTH, callback=callback_function, bouncetime=300)

try:
    print("Waiting for interrupt...")
    # Do something to keep the script running
    while True:
        time.sleep(0.1)  # Sleep to reduce CPU usage

except KeyboardInterrupt:
    # Clean up GPIO on keyboard interrupt
    GPIO.cleanup()
