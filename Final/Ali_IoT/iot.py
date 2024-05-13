#!/usr/bin/python3

import aliLink,mqttd,rpi
import time,json,serial,requests

def Get_position():
    ser=serial.Serial("/dev/ttyUSB1",115200)
    while True:
        line=str(ser.readline())
        GPGGA_line = line
        if GPGGA_line.startswith("b'$GPGGA"):
            #print(GPGGA_line)
            GPGGA_line = str(GPGGA_line).split(',')
            #print(GPGGA_line) 
            latitude=float(GPGGA_line[2][:2]) + float(GPGGA_line[2][2:])/60
            longitude=float(GPGGA_line[4][:3]) + float(GPGGA_line[4][3:])/60
            return latitude, longitude

# 消息回调（云端下发消息的回调函数）
def on_message(client, userdata, msg):
    try:
        Msg = json.loads(msg.payload)
        switch = Msg['params']['PowerLed']
        rpi.powerLed(switch)
    except Exception as e:
        print(e)
    print(msg.payload)  # 开关值

#连接回调（与阿里云建立链接后的回调函数）
def on_connect(client, userdata, flags, rc):
    pass

def iot_process():
    
    ProductKey = 'k0mhlroR224'
    DeviceName = 'wyy1'
    DeviceSecret = "2b1536dbf3227336c6bd63a8a5c4cedf"
    # topic (iot后台获取)
    POST = '/sys/k0mhlroR224/wyy1/thing/event/property/post'  # 上报消息到云
    POST_REPLY = '/sys/k0mhlroR224/wyy1/thing/event/property/post_reply'  
    SET = '/sys/k0mhlroR224/wyy1/thing/service/property/set'  # 订阅云端指令

    # 链接信息
    Server,ClientId,userNmae,Password = aliLink.linkiot(DeviceName,ProductKey,DeviceSecret)

    # mqtt链接
    mqtt = mqttd.MQTT(Server,ClientId,userNmae,Password)
    mqtt.subscribe(SET) # 订阅服务器下发消息topic
    mqtt.begin(on_message,on_connect)


    # 信息获取上报，每10秒钟上报一次系统参数
    while True:
        time.sleep(2)
        
        CPU_temp = float(rpi.getCPUtemperature())
        CPU_usage = float(rpi.getCPUuse()) 
        
        latitude, longitude = Get_position() # 地理信息
    
        # 构建与云端模型一致的消息结构
        updateMsn = {
            'cpu_temperature':CPU_temp,
            'Longitude':longitude,
            'Latitude':latitude
        }
        JsonUpdataMsn = aliLink.Alink(updateMsn)
        print(JsonUpdataMsn)

        mqtt.push(POST,JsonUpdataMsn) # 定时向阿里云IOT推送数据


if __name__ == "__main__":
    iot_process()
