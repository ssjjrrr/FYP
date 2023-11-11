import RPi.GPIO as GPIO
import time
import multiprocessing as mp
from multiprocessing import Manager

def init_ultrasonic_sensor(trig, echo):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trig, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(echo, GPIO.IN)

def init_buzzer(trig):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trig, GPIO.OUT, initial = GPIO.LOW)

def us_get_distance(trig, echo):
    pulse_start = 0
    pulse_end = 0

    timeout = 0.1
    start_time = time.time()

    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(trig, GPIO.LOW)

    while GPIO.input(echo) == 0:
        pulse_start = time.time()
        if time.time() - start_time > timeout:
            break

    while GPIO.input(echo) == 1:
        pulse_end = time.time()
        if time.time() - start_time > timeout:
            break
    if pulse_start == 0 or pulse_end == 0:
        return -1
    
    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 34000 / 2, 5)
    return distance

def ultrasonic_sensor_process(trig1, trig2 , echo1, echo2, distance_value):
    init_ultrasonic_sensor(trig1, echo1)
    init_ultrasonic_sensor(trig2, echo2)

    while True:
        distance1 = us_get_distance(trig1, echo1)
        distance2 = us_get_distance(trig2, echo2)
        distance_value.value = min(distance1, distance2)
        print(distance_value.value)
        time.sleep(0.2)

def buzzer_trigger_process(trig, distance_value):
    init_buzzer(trig)
    while True:
        distance = distance_value.value
        if 40 < distance < 50:
            GPIO.output(trig, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(trig, GPIO.LOW)
            time.sleep(0.5)
        elif 30 <distance <= 40:
            GPIO.output(trig, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(trig, GPIO.LOW)
            time.sleep(0.4)
        elif 20 <distance <= 30:
            GPIO.output(trig, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(trig, GPIO.LOW)
            time.sleep(0.2)
        elif distance <= 20:
            GPIO.output(trig, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(trig, GPIO.LOW)
            time.sleep(0.1)
        else:
            GPIO.output(trig, GPIO.LOW)
            time.sleep(0.2)

if __name__ == "__main__":
    ustrig = [14,23]
    usecho = [15,24]
    bztrig = 25

    distance_value = mp.Value("f",0)

    us_process = mp.Process(target=ultrasonic_sensor_process, args=(ustrig[0], ustrig[1], usecho[0], usecho[1], distance_value))
    bz_process = mp.Process(target=buzzer_trigger_process, args=(bztrig, distance_value))

    us_process.start()
    bz_process.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        us_process.terminate()
        us_process.join()

        bz_process.terminate()
        bz_process.join()
        GPIO.cleanup()
