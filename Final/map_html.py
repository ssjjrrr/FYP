import pymysql.cursors
import serial
import time
import folium
import datetime
import os

def get_location():
    ser = serial.Serial("/dev/ttyUSB1", 115200)
    while True:
        line = str(ser.readline())
        GPGGA_line = line
        if GPGGA_line.startswith("b'$GPGGA"):
            GPGGA_line = str(GPGGA_line).split(',')
            global latitude
            global longitude
            latitude = float(GPGGA_line[2][:2]) + float(GPGGA_line[2][2:]) / 60
            longitude = float(GPGGA_line[4][:3]) + float(GPGGA_line[4][3:]) / 60
            return (latitude, longitude)

def open_GPS(port='/dev/ttyUSB2', baud_rate=115200):
    ser = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(1)
    ser.write(b'AT+QGPS=1\r')
    time.sleep(1)

# 创建地图对象
def map_process():
    open_GPS()
    map_obj = folium.Map(location=[0, 0], zoom_start=10)  # 初始化地图

    while True:
        # 获取位置信息
        latitude, longitude = get_location()
        map_obj = folium.Map(location=[latitude, longitude], zoom_start=10)
        folium.Marker([latitude, longitude], tooltip='Your Location').add_to(map_obj)
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"/home/admin/Desktop/FYP/FYP/Final/map_saved/location_map_{current_time}.html"

        # 保存地图为HTML文件
        map_obj.save(file_name)
        # 等待5秒
        time.sleep(5)
