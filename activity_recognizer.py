# this program recognizes activities
import os
from glob import glob
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.preprocessing import scale, MinMaxScaler
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
from joblib import dump, load

DATA_PATH = "data"
MODEL_PATH = "svm_model.joblib"

x_train = None
x_test = None
y_train = None
y_test = None

#Load all the datasets, phew
def load_data():
    all_datasets = []
    for activity in os.listdir(DATA_PATH):
        current_activity = os.path.join(DATA_PATH, activity)
        for files in glob(f"{current_activity}/*.csv"):
            df = pd.read_csv(files, on_bad_lines='skip')
            df['activity'] = activity
            all_datasets.append(df)
    print("Data loaded.")
    return pd.concat(all_datasets, ignore_index=True)

def pre_process_data(df):
    #filter out id, turn activities into numbers
    #[['timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']]
    df['activity_num'] = 0
    df.loc[df['activity'] == 'lifting', 'activity_num'] = 1
    df.loc[df['activity'] == 'running', 'activity_num'] = 2
    df.loc[df['activity'] == 'rowing', 'activity_num'] = 3
    df = df.dropna()
    filtered_df = df[['timestamp', 'acc_x', 'acc_y', 'acc_z', 'activity_num']]
    
    #Mean Removal
    scaled_df = scale(filtered_df[['acc_x', 'acc_y', 'acc_z']])
    subset_mean = filtered_df.copy()
    subset_mean[['acc_x', 'acc_y', 'acc_z']] = scaled_df
    #Normalization
    scaler = MinMaxScaler()
    scaler.fit(subset_mean[['acc_x', 'acc_y', 'acc_z']])
    scaled_samples = scaler.transform(subset_mean[['acc_x', 'acc_y', 'acc_z']])
    df_normalized = subset_mean.copy()
    df_normalized[['acc_x', 'acc_y', 'acc_z']] = scaled_df

    print("Data preprocessed.")
    return df_normalized

#Visualizing the data, I could see that the acc data seems easy-ish to distinguish, while the gyro seems not.
#Thus, I will try to omit the gyro data for increased performance, hoping that the acc data alone is good enough.
#Also, I have problems with DIPPID data that has been put into Arrays being stale when accessed from another method.
#I will have asked about this on Thursday, unless I forgot. If I did, please write me a mail or contact me on Discord!
def visualize_data(df):
    sns.pairplot(df, hue='activity_num', vars=['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])
    plt.show()

def split_data(df):
    global x_train, x_test, y_train, y_test
    x = df[['acc_x', 'acc_y', 'acc_z']]
    y = df['activity_num']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y)
    print("Data split.")


def train_model(df):
    #poly=75%avg,  rbf=83%avg,   sigmoid=48%avg,   linear=71%avg   (mit allen 3 Achsen bei acc)
    #poly=51%avg,  rbf=72%avg,   sigmoid=35%avg,   linear=61%avg   (mit y und z Achse bei acc)
    classifier = svm.SVC(kernel='rbf')
    classifier.fit(x_train, y_train)
    return classifier

def test_accuracy(clf):
    print("Currently evaluating test data, please wait a bit...")
    y_pred = clf.predict(x_test)
    print("Accuracy value: ", accuracy_score(y_test, y_pred))


activity_df = load_data()
processed_df = pre_process_data(activity_df)
#print(processed_df)
#visualize_data(processed_df)
split_data(processed_df)

#model = train_model(processed_df)
#dump(model, MODEL_PATH)
model = load(MODEL_PATH)
print("Model loaded.")
test_accuracy(model)


def evaluate_data(acc_data: pd.DataFrame):
    #Mean removal
    scaled_acc_data = scale(acc_data[['acc_x', 'acc_y', 'acc_z']])
    acc_data_mean = acc_data.copy()
    acc_data_mean[['acc_x', 'acc_y', 'acc_z']] = scaled_acc_data
    #Normalization
    scaler = MinMaxScaler()
    scaler.fit(acc_data_mean[['acc_x', 'acc_y', 'acc_z']])
    scaled_samples = scaler.transform(acc_data_mean[['acc_x', 'acc_y', 'acc_z']])
    acc_data_normalized = acc_data_mean.copy()
    acc_data_normalized[['acc_x', 'acc_y', 'acc_z']] = scaled_acc_data
    
    prediction = model.predict(acc_data_normalized)
    return prediction


    