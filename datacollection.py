import serial
import Adafruit_DHT
import time
from pymongo import MongoClient

# MongoDB 设置
uri = "mongodb+srv://yangl125912:Whbc2020@cluster0.hfcxcyf.mongodb.net/"
client = MongoClient(uri)
db = client['monitordb']
collection = db['mycollection']
# DHT11 设置
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# 串行通信设置
ser = serial.Serial('/dev/ttyACM0', 9600) # 端口可能需要根据你的设置进行调整

while True:
    # 读取 DHT11 数据
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
    else:
        print("Sensor failure. Check wiring.")

    # 读取水位传感器数据
    if ser.in_waiting > 0:
        water_level = ser.readline().decode('utf-8').rstrip()
        print("Sensor value: ", water_level)

        # 构建数据字典
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "water_level": water_level,
            "timestamp": time.time()
        }

        # 插入数据到 MongoDB
        collection.insert_one(data)

    time.sleep(5)
