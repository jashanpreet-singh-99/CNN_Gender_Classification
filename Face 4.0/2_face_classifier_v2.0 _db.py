from tensorflow import keras
import numpy as np
import os
import cv2 as cv
import pandas as pd
import concurrent.futures

model = keras.models.load_model('keras_model.keras')

IMG_PATH = os.path.join(os.getcwd(), "raw_faces")
DB_PATH = os.path.join(os.getcwd(), "classification_db")

if not os.path.isdir(DB_PATH):
        os.mkdir(DB_PATH)

dataset_x = []

BATCH_SIZE = 5000

processed_so_far = 0

batch_count = 0

print("Loading Images ... ")
parent_id_list = os.listdir(IMG_PATH)
list_d = []
for i,parent_id in enumerate(parent_id_list):
        print("Parent ID : ", i)
        pk_list = os.listdir(os.path.join(IMG_PATH, parent_id))
        for pk in pk_list:
                img_list = os.listdir(os.path.join(IMG_PATH, parent_id, pk))
                for img in img_list:
                        dic = {}
                        dic['parent_id'] = parent_id
                        dic['pk'] = pk
                        dic['img'] = img
                        list_d.append(dic)
print("Images Loaded : ", len(list_d))
dataframe = pd.DataFrame(list_d)
dataframe.to_csv(os.path.join(DB_PATH, "DF_db.csv"))

print("Raw database saved.")
master_labels = []

for i,row in dataframe.iterrows():
        path = os.path.join(IMG_PATH, row['parent_id'], row['pk'], row['img'])
        img = cv.imread(path, 0)
        img = img/255.0
        dataset_x.append(img)
        if (i % BATCH_SIZE) == 0 and i - processed_so_far >= BATCH_SIZE :
                dataset_x = np.asarray(dataset_x)
                print("Dataset Loaded running Model for predictions. At cursor : ", i)
                labels = model.predict(dataset_x)
                labels = labels.argmax(axis=1)
                print("Classification complete.")
                master_labels.extend(labels)
                processed_so_far += BATCH_SIZE
                print("Clearing old dataset_x.")
                dataset_x = []
        else :
                print(i)

if len(dataset_x) > 0 :
        dataset_x = np.asarray(dataset_x)
        print("Dataset Loaded running Model for predictions. At cursor : ", processed_so_far)
        labels = model.predict(dataset_x)
        labels = labels.argmax(axis=1)
        print("Classification complete.")
        master_labels.extend(labels)

print(len(master_labels), "==", len(dataframe))
dataframe['classification'] = master_labels
dataframe['mode'] = 'D'
print(dataframe.head())
dataframe.to_csv(os.path.join(DB_PATH, "DF_db.csv"))
input("Press any key to exit.")
