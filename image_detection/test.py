import RPi.GPIO as GPIO
import time

sensor = 36
buzzer = 35

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor,GPIO.IN)
GPIO.setup(buzzer,GPIO.OUT)

GPIO.output(buzzer,False)
print ("IR Sensor Ready.....")
print (" ")

try:
   while True:
      if GPIO.input(sensor):
          GPIO.output(buzzer,False)
          print ("Object not Detected")
          while GPIO.input(sensor):
              time.sleep(0.2)
      else:
          GPIO.output(buzzer,True)
          print ("Object Detected")

except KeyboardInterrupt:
    GPIO.cleanup()
