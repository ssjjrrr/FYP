import RPi.GPIO as GPIO
import time

def init_ultrasonic_sensor(): # initialize GPIO
	TRIG = [14,23]
	ECHO = [15,24]
	GPIO.setmode(GPIO.BCM)
	
	for i in range(2):
		GPIO.setup(TRIG[i], GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(ECHO[i], GPIO.IN)
	# time.sleep(2)
	return TRIG, ECHO
     
def get_distance(trig,echo):
	pulse_start = 0
	pulse_end = 0
	
	timeout = 0.1 # for determine if a timeout situation occurs
	start_time = time.time()
	
	GPIO.output(trig,GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(trig,GPIO.LOW)

	while GPIO.input(echo) == 0: # receive echo signal
		pulse_start = time.time()
		if time.time() - start_time > timeout:
			break;    
	while GPIO.input(echo) == 1: # signal disappear
		pulse_end = time.time()
		if time.time() - start_time > timeout:
			break;
	if pulse_start == 0 or pulse_end == 0: # time out
		return -1
		
	pulse_duration = pulse_end - pulse_start
	
	distance = round(pulse_duration*34000/2,5) # calculate the distance
	return distance
	


