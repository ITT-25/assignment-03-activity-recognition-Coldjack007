# this program visualizes activities with pyglet
import activity_recognizer as activity
import os
import numpy as np
import pandas as pd
import time
import pyglet
import DIPPID
import random

PORT = 5700
sensor = DIPPID.SensorUDP(PORT)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

win = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

is_mainMenu = True
is_Training = False
game_quit_message = pyglet.text.Label("Press P to return to the menu and Q to quit the game.", WINDOW_WIDTH/2, WINDOW_HEIGHT-10, anchor_x="center", anchor_y="center", font_name="Times New Roman", font_size=14)
mainMenu_message1 = pyglet.text.Label("Press Q to quit the game.", WINDOW_WIDTH/2, WINDOW_HEIGHT-10, anchor_x="center", anchor_y="center", font_name="Times New Roman", font_size=14)
mainMenu_message2 = pyglet.text.Label("Press Button 1 on your DIPPID device to start!", WINDOW_WIDTH/2, WINDOW_HEIGHT/2, anchor_x="center", anchor_y="center", font_name="Times New Roman", font_size=26)

exercise_msg1 = pyglet.text.Label("Current exercise: ", WINDOW_WIDTH/2, WINDOW_HEIGHT/2, anchor_x="center", anchor_y="center", font_name="Times New Roman", font_size=26)
exercise_msg2 = pyglet.text.Label("0 out of 3 reps done!", WINDOW_WIDTH/2, WINDOW_HEIGHT/2-30, anchor_x="center", anchor_y="center", font_name="Times New Roman", font_size=12)

all_activities = ['lifting', 'rowing', 'running', 'jumpingjacks']
current_activity = ""
current_activity_num = 0

current_score = 0
MAX_SCORE = 3
confidence = 0
CONFIDENCE_THRESHOLD = 100

current_x_data = []
current_y_data = []
current_z_data = []
DATA_COLLECTION_FREQUENCY = 1/100
current_time = time.time()

def get_next_activity():
    global current_activity, current_activity_num
    activity_num = random.randint(0,3)
    current_activity = all_activities[activity_num]
    current_activity_num = activity_num

def init_game():
    get_next_activity()

def start_game(data):
    global is_Training, is_mainMenu
    if is_mainMenu is False:
        pass
    is_Training = True
    is_mainMenu = False

def handle_data(data):
    global current_time, confidence, current_score
    if is_Training is True:
        if current_time - DATA_COLLECTION_FREQUENCY < time.time():
            current_time = time.time()
            current_x_data.append(data['x'])
            current_y_data.append(data['y'])
            current_z_data.append(data['z'])
            if len(current_x_data) == 200:
                full_data = np.array([current_x_data, current_y_data, current_z_data])
                pd_data = pd.DataFrame(full_data).T
                pd_data.columns = ['acc_x', 'acc_y', 'acc_z']
                answer = activity.evaluate_data(pd_data)
                print(answer)
                for evaL_answer in range(len(answer)):
                    if answer[evaL_answer] == current_activity_num:
                        confidence += 1
                if confidence >= CONFIDENCE_THRESHOLD:
                    current_score += 1
                if current_score == MAX_SCORE:
                    get_next_activity()
                    current_score = 0
                print("Confidence: " + str(confidence))
                confidence = 0
                current_x_data.clear()
                current_y_data.clear()
                current_z_data.clear()

def update_ui():
    exercise_msg1.text = "Current exercise: " + all_activities[current_activity_num]
    exercise_msg2.text = str(current_score) + " out of " + str(MAX_SCORE) + " done!"

def exit_game():
    global is_Training, is_mainMenu
    if is_mainMenu is True:
        pass
    is_Training = False
    is_mainMenu = True

sensor.register_callback("button_1", start_game)
sensor.register_callback("accelerometer", handle_data)
init_game()

@win.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        os._exit(0)
    if symbol == pyglet.window.key.P:
        exit_game()

@win.event
def on_draw():
    win.clear()
    if is_mainMenu:
        mainMenu_message1.draw()
        mainMenu_message2.draw()
    elif is_Training:
        update_ui()
        game_quit_message.draw()
        exercise_msg1.draw()
        exercise_msg2.draw()

pyglet.app.run()

while True:
    time.sleep(0.001)