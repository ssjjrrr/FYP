import serial
import time

def send_sms(port, baud_rate, phone_number, message):
    ser = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(1)

    ser.write(b'AT+CMGF=1\r')
    time.sleep(1)

    ser.write(b'AT+CMGS="' + phone_number.encode() + b'"\r')
    time.sleep(1)

    ser.write(message.encode() + b"\r")
    time.sleep(1)

    ser.write(bytes([26]))
    time.sleep(1)

    ser.close()

def message_process():
    port = '/dev/ttyUSB2'
    baud_rate = 115200
    phone_number = '15919979280'
    message = 'SOS'
    
    send_sms(port, baud_rate, phone_number, message)
    
if __name__ == "__main__":
    message_process()
