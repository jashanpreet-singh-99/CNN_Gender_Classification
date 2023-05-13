import os
import cv2 as cv
import pandas as pd

DB_PATH = os.path.join(os.getcwd(), 'classification_db', "DF_db_v1.0.csv")
DB_DF_PATH = os.path.join(os.getcwd(), 'classification_db', "DF_db_MODEL.csv")

dataframe_manual = pd.read_csv(DB_PATH, index_col=0)
dataframe_pred = pd.read_csv(DB_DF_PATH, index_col=0)

df_remov = dataframe_manual[dataframe_manual['classification'] == -1]
remove_indexes = list(df_remov.index)
print("Indexed to Remove : ",len(remove_indexes))

""" Remove invalid entries """
dataframe_manual.drop(remove_indexes,inplace=True)
dataframe_pred.drop(remove_indexes,inplace=True)
print("Enteires to evaluate : ", len(dataframe_manual))

values = list(dataframe_manual['classification'] == dataframe_pred['classification'])
accuracy = sum(values)/len(values) * 100

print("Model Accuracy : ", accuracy)
