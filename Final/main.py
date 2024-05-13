import RPi.GPIO as GPIO
import time
import multiprocessing as mp
import smbus
import FYP.Final.detect_lite as detect_lite
import map_html
import message
import sql_connect as sql
from Ali_IoT import iot, ali_message

def run_video_process():
    detect_lite.video_process()

def run_iot_process():
    iot.iot_process()

def run_map_process():
    map_html.map_process()

def run_message_process():
	message.message_process()
    
def run_sql_process():
    sql.sql_process()
    
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
    time.sleep(0.00001)
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
        #print(distance_value.value)
        time.sleep(0.2)

def water_sensor_process(address, bus_id, channel, water_voltage_threshold, in_water):
    while True:
        bus = smbus.SMBus(bus_id)
        water_detect_voltage = bus.read_byte(address) * 5 / 255
        print(water_detect_voltage)
        if water_detect_voltage < water_voltage_threshold:
            in_water.value = False
        else:
            in_water.value = True
        #print(in_water.value)
        time.sleep(0.5)

def buzzer_trigger_process(trig, distance_value, in_water):
    init_buzzer(trig)
    while True:
        if in_water.value == True:
            GPIO.output(trig, GPIO.HIGH)
            time.sleep(0.5)
        else:
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

    address = 0x48
    bus_id = 1
    channel = 0x00
    water_voltage_threshold = 2.5
    
    distance_value = mp.Value("f",0)
    in_water = mp.Value("i", False)
    

    us_process = mp.Process(target=ultrasonic_sensor_process, args=(ustrig[0], ustrig[1], usecho[0], usecho[1], distance_value))
    bz_process = mp.Process(target=buzzer_trigger_process, args=(bztrig, distance_value, in_water))
    ws_process = mp.Process(target=water_sensor_process, args=(address, bus_id, channel, water_voltage_threshold, in_water))
    video_process = mp.Process(target=run_video_process)
    map_process = mp.Process(target=run_map_process)
    # iot_process = mp.Process(target=run_iot_process)
    message_process = mp.Process(target=run_message_process)
    sql_process = mp.Process(target=run_sql_process)
    all_process = [us_process, bz_process, ws_process, video_process, map_process, message_process, sql_process]
    
    for process in all_process:
        process.start()
    
    # us_process.start()
    # bz_process.start()
    # ws_process.start()
    # video_process.start()
    # map_process.start()
    # iot_process.start()
    # message_process.start()
    # sql_process.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        for process in all_process:
            process.terminate()
            process.join()
        # us_process.terminate()
        # us_process.join()
        
        # bz_process.terminate()
        # bz_process.join()
        
        # ws_process.terminate()
        # ws_process.join()
        
        # video_process.terminate()
        # video_process.join()
        
        # map_process.terminate()
        # map_process.join()
        
        # iot_process.terminate()
        # iot_process.join()
        
        # message_process.terminate()
        # message_process.join()
        
        GPIO.cleanup()
