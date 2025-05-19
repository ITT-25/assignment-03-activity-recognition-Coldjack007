# this program gathers sensor data
from DIPPID import SensorUDP
import time
import pandas as pd

PORT = 5700
sensor = SensorUDP(PORT)

MY_NAME = "richard"
ACTIVITY = "jumpingjacks"
NUMBER = "5"

button_pressed = False
starting_time = time.time()
TIMER = 10.01

#Arrays
timestamp = []
acc_x = []
acc_y = []
acc_z = []
gyro_x = []
gyro_y = []
gyro_z = []

def handle_button_press(data):
    global button_pressed, starting_time, id_num
    if not button_pressed:
        button_pressed = True
        
def export_csv():
    csv_dict = {'timestamp': timestamp, 'acc_x': acc_x, 'acc_y': acc_y, 'acc_z': acc_z, 'gyro_x': gyro_x, 'gyro_y': gyro_y, 'gyro_z': gyro_z}
    df = pd.DataFrame(csv_dict)
    df.to_csv(MY_NAME + "-" + ACTIVITY + "-" + NUMBER + ".csv", index=False)

sensor.register_callback('button_1', handle_button_press)

while True:
    if button_pressed:
        starting_time = time.time()
        while time.time() - starting_time < TIMER:
            timestamp.append(time.time())
            acc_x.append(sensor.get_value('accelerometer')['x'])
            acc_y.append(sensor.get_value('accelerometer')['y'])
            acc_z.append(sensor.get_value('accelerometer')['z'])
            gyro_x.append(sensor.get_value('gyroscope')['x'])
            gyro_y.append(sensor.get_value('gyroscope')['y'])
            gyro_z.append(sensor.get_value('gyroscope')['z'])
            print("Data recorded: " + str(id_num))
            id_num += 1
        export_csv()
        button_pressed = False
    time.sleep(0.000001)