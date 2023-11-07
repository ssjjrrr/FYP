import RPi.GPIO as GPIO
import asyncio
import time

def init_buzzer():
    TRIG = 25
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.HIGH)
    return TRIG

def buzzer_trigger(trig,rate = 1):
        GPIO.output(trig,GPIO.LOW) 
        time.sleep(1/rate)
        
        GPIO.output(trig,GPIO.HIGH)
        time.sleep(1/rate)
