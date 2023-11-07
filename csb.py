import RPi.GPIO as GPIO
import time

TRIG = 24
ECHO = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT,initial = GPIO.LOW)
GPIO.setup(ECHO,GPIO.IN)
time.sleep(2)

def get_distance(ECHO):
	while not GPIO.input(ECHO):
		pass

	t1 = time.time()
	while GPIO.input(ECHO):
		pass
	t2 = time.time()
	distance = round((t2-t1)*340/2,5)
	return distance

for i in range(20):
	GPIO.output(TRIG,GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(TRIG,GPIO.LOW)
	
	distance = get_distance(ECHO)

	print("now distance is:",distance)
	time.sleep(1)
GPIO.cleanup()
