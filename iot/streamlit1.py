import streamlit as st
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime
import numpy as np
import time
#from pushbullet import Pushbullet

# 数据解析、清理和平滑的函数可以从之前的脚本中直接复制过来

# Streamlit Web 应用的主函数

    # 设置 MongoDB 连接
uri = "mongodb+srv://yangl125912:Whbc2020@cluster0.hfcxcyf.mongodb.net/"
client = MongoClient(uri)

    # 连接到数据库和集合
db_temperature = client['temperature_database']
collection_temperature = db_temperature['temperature_data']
db_humidity = client['humidity_database']
collection_humidity = db_humidity['humidity_data']
db_water_level = client['water_level_database']
collection_water_level = db_water_level['water_level_data']


    # 获取历史温度数据
temperature_records = collection_temperature.find().sort('timestamp', 1)
temperatures_history = [record['temperature'] for record in temperature_records]

# 获取历史湿度数据
humidity_records = collection_humidity.find().sort('timestamp', 1)
humidities_history = [record['humidity'] for record in humidity_records]

# 获取历史水位数据
water_level_records = collection_water_level.find().sort('timestamp', 1)
water_levels_history = [record['water_level'] for record in water_level_records]

    # # 获取数据
temperatures = list(collection_temperature.find({}, {'_id': 0, 'temperature': 1, 'timestamp': 1}))
humidities = list(collection_humidity.find({}, {'_id': 0, 'humidity': 1, 'timestamp': 1}))
water_levels = list(collection_water_level.find({}, {'_id': 0, 'water_level': 1, 'timestamp': 1}))



# 解析数据
def parse_data(data_list, value_key):
    timestamps = [datetime.strptime(d['timestamp'], '%Y-%m-%d %H:%M:%S') for d in data_list]
    values = [d[value_key] for d in data_list]
    return timestamps, values

# 移动平均函数
def moving_average(data, window_size):
    weights = np.ones(window_size) / window_size
    return np.convolve(data, weights, mode='valid')

# 使用移动平均平滑数据
def smooth_data(values, window_size):
    return moving_average(values, window_size)

# 设置移动平均的窗口大小
WINDOW_SIZE = 30

def clean_data(data_list, value_key, low_threshold, high_threshold):
    cleaned_data = [d for d in data_list if low_threshold <= d[value_key] <= high_threshold]
    return cleaned_data

# 检查温度是否正常
def check_temperature(temperature):
    if temperature > 28:
        return "It's a bit hot, open the window or turn off the heater"
    if temperature < 22: 
        return "It's a bit cold, close the window or turn on the heater" 
    else:
        return "comfortable temp"
# 检查湿度是否正常
def check_humidity(humidity):
        
    if humidity > 60:
        return "It's a bit wet, close the window or turn on the heater"
    if humidity < 50: 
        return "It's a bit dry, open the window or turn off the heater" 
    else:
        return "comfortable humidity"
# 检查水位是否正常
def check_water_level(water_level):
    return "normal" if water_level <= 300 else "Please pour some water"

def is_clothes_dry(temperatures, humidities, water_levels):
    # 假设 temperatures, humidities, water_levels 是列表，包含历史数据
    if not temperatures_history or not humidities_history or not water_levels_history:
        return False

    # 检查温度是否上升
    temperature_rising = temperatures_history[-1] >= temperatures_history[-2]

    # 检查湿度是否降至最低
    humidity_at_lowest = humidities_history[-1] >= temperatures_history[-2]

    # 检查水位是否下降
    water_level_dropping = water_levels_history[-1] <= water_levels_history[-2]

    return temperature_rising and humidity_at_lowest and water_level_dropping

#def send_push_notification(title, body):
    # 替换为你的 Pushbullet Access Token
    pb = Pushbullet("o.WUmcdIqP5jiXtidmo1hKAFpODJlRlt3P")
    pb.push_note(title, body)

# 数据监测页面
def data_monitoring_page():
    st.title("Room and clothes condition")

    latest_temp_data = collection_temperature.find().sort('timestamp', -1).limit(1)
    latest_temp = latest_temp_data[0]['temperature'] if latest_temp_data else None

# 获取最新的湿度数据
    latest_hum_data = collection_humidity.find().sort('timestamp', -1).limit(1)
    latest_hum = latest_hum_data[0]['humidity'] if latest_hum_data else None

# 获取最新的水位数据
    latest_water_data = collection_water_level.find().sort('timestamp', -1).limit(1)
    latest_water = latest_water_data[0]['water_level'] if latest_water_data else None

    #st.write(f"Temperature：{latest_temp}°C - {check_temperature(latest_temp)}")
    #st.write(f"Humidity：{latest_hum}% - {check_humidity(latest_hum)}")
    #st.write(f"Water Level：{latest_water} - {check_water_level(latest_water)}")
    st.markdown("<h1 style='text-align: center;'>🌡️ Temperature Monitoring🌡️</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>💧 Humidity Monitoring 💧</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>🌊 Water Level Monitoring 🌊</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        temp_status = check_temperature(latest_temp)
        temp_color = "normal" if temp_status == "comfortable temp" else "inverse"
        st.metric(label="Temperature", value=f"{latest_temp}°C", delta=temp_status, delta_color=temp_color)
        st.markdown("🌡️", unsafe_allow_html=True)


    with col2:
        hum_status = check_humidity(latest_hum)
        hum_color = "normal" if hum_status == "comfortable humidity" else "inverse"
        st.metric(label="Humidity", value=f"{latest_hum}%", delta=hum_status, delta_color=hum_color)
        st.markdown("💧", unsafe_allow_html=True)

    with col3:
        water_status = check_water_level(latest_water)
        water_color = "normal" if water_status == "normal" else "inverse"
        st.metric(label="Water level", value=f"{latest_water}", delta=water_status, delta_color=water_color)
        st.markdown("🌊", unsafe_allow_html=True)

    if is_clothes_dry(temperatures, humidities, water_levels):
        st.success("Clothes is dry!！")
        #send_push_notification("Clothes is dry", "Remember to take them before deformation")
    else:
        st.info("CLothes is drying...")

    update_interval = 120  # 秒为单位

    st.write(f"Next update in {update_interval} seconds.")
    time.sleep(update_interval)
    st.experimental_rerun()

def data_visualization_page():
    st.title("Conditions flow map")
    
    TEMP_LOW_THRESHOLD = 19
    TEMP_HIGH_THRESHOLD = 50
    HUM_LOW_THRESHOLD = 35
    HUM_HIGH_THRESHOLD = 100
    WATER_LOW_THRESHOLD = 100
    WATER_HIGH_THRESHOLD = 200

# 清理数据
    temperatures_cleaned = clean_data(temperatures, 'temperature', TEMP_LOW_THRESHOLD, TEMP_HIGH_THRESHOLD)
    humidities_cleaned = clean_data(humidities, 'humidity', HUM_LOW_THRESHOLD, HUM_HIGH_THRESHOLD)
    water_levels_cleaned = clean_data(water_levels, 'water_level', WATER_LOW_THRESHOLD, WATER_HIGH_THRESHOLD)

# 重新解析清理后的数据
    temp_times, temp_values = parse_data(temperatures_cleaned, 'temperature')
    hum_times, hum_values = parse_data(humidities_cleaned, 'humidity')
    water_times, water_values = parse_data(water_levels_cleaned, 'water_level')

# 平滑后的数据
    temp_values_smoothed = smooth_data(temp_values, WINDOW_SIZE)    
    hum_values_smoothed = smooth_data(hum_values, WINDOW_SIZE)
    water_values_smoothed = smooth_data(water_values, WINDOW_SIZE)

# 为了匹配平滑后的数据长度，我们需要调整时间戳的数组
    temp_times = temp_times[:len(temp_values_smoothed)]
    hum_times = hum_times[:len(hum_values_smoothed)]
    water_times = water_times[:len(water_values_smoothed)]

    fig_size = (16,4)

    # 用 Streamlit 显示图表
    st.subheader('Temperature')
    fig, ax = plt.subplots(figsize=fig_size)
    ax.plot(temp_times, temp_values_smoothed, label='Temperature')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Temperature (C)')
    ax.legend()
    st.pyplot(fig)

    st.subheader('Humidity')
    fig, ax = plt.subplots(figsize=fig_size)
    ax.plot(hum_times, hum_values_smoothed, label='Humidity')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Humidity (%)')
    ax.legend()
    st.pyplot(fig)

    st.subheader('Water Level')
    fig, ax = plt.subplots(figsize=fig_size)
    ax.plot(water_times, water_values_smoothed, label='Water Level')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Water Level')
    ax.legend()
    st.pyplot(fig)

    update_interval = 120  # 秒为单位

    # Streamlit 应用将在达到时间间隔后重新运行
    st.write(f"Next update in {update_interval} seconds.")
    time.sleep(update_interval)
    st.experimental_rerun()

if st.button('Send Notification'):
    send_push_notification("Hello", "This is a test notification from Streamlit!")
    st.success("Notification sent!")

def main():
    # 页面选择
    page = st.sidebar.selectbox("MENU", ["Room and clothes condition", "Conditions flow map"])

    if page == "Room and clothes condition":
        data_monitoring_page()
    elif page == "Conditions flow map":
        data_visualization_page()    

if __name__ == "__main__":
    main()