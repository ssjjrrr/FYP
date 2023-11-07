import csb2 as csb
import RPi.GPIO as GPIO
import time

TRIG, ECHO = csb.init_GPIO()

for i in range(20):
	distance1 = csb.get_distance(TRIG[0],ECHO[0])
	distance2 = csb.get_distance(TRIG[1],ECHO[1])

	print(f"sensor1:{distance1}cm")
	print(f"sensor2:{distance2}cm")
	time.sleep(0.5)
	
GPIO.cleanup()