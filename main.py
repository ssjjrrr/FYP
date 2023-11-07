import ultrasonic_sensor as us
import buzzer as bz
import RPi.GPIO as GPIO
import time
import asyncio

ustrig, usecho = us.init_ultrasonic_sensor()
bztrig = bz.init_buzzer()
time.sleep(2)

distance_threashold = 40

while True:
	distance1 = us.get_distance(ustrig[0],usecho[0])
	distance2 = us.get_distance(ustrig[1],usecho[1])
	
	distance_min = min(distance1,distance2)
	if distance_min < distance_threashold:
		rate = distance_threashold-distance_min
		print("buzzer is triggered")
		bz.buzzer_trigger(bztrig, rate if rate > 1 else 1)

	print(f"sensor1:{distance1}cm")
	print(f"sensor2:{distance2}cm")
	time.sleep(0.2)
	
GPIO.cleanup()
