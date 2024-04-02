import pymysql.cursors
import serial
import time

def get_location():
    ser=serial.Serial("/dev/ttyUSB1",115200)
    while True:
        line=str(ser.readline())
        GPGGA_line = line
        if GPGGA_line.startswith("b'$GPGGA"):
            GPGGA_line = str(GPGGA_line).split(',')
            global latitude
            global longitude
            latitude=float(GPGGA_line[2][:2]) + float(GPGGA_line[2][2:])/60
            longitude=float(GPGGA_line[4][:3]) + float(GPGGA_line[4][3:])/60
            return(latitude, longitude)

def sql_process():
    connect = pymysql.Connect(
        host='172.25.5.203',
        port=3306,
        user='root',
        passwd='001213',
        db='test_1',
        charset='utf8'
    )

    # 获取游标
    cursor = connect.cursor()
    #创建表格
    sql = "CREATE TABLE location(latitude DOUBLE,longitude DOUBLE)"
    try:
        cursor.execute(sql)
        connect.commit()
    except:
        print("表已存在")
    print('成功创建表格')


    # 插入数据
    while True:
        get_location()
        sql = "INSERT INTO location VALUES(%f, %f)"
        data = (latitude, longitude)
        try:
            cursor.execute(sql % data)
            connect.commit()
            print('成功插入', cursor.rowcount, '条数据')
        except Exception as e:
            print(f"插入数据时发生错误: {e}")
        time.sleep(2)
