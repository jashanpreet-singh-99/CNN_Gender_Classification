import os
import cv2 as cv
import pandas as pd

DB_PATH = os.path.join(os.getcwd(), 'classification_db', "DF_db_v1.0.csv")
IMG_PATH = os.path.join(os.getcwd(), 'raw_faces')
SAVE_PATH = os.path.join(os.getcwd(), 'db_images')
CHECK_PATH = os.path.join(DB_PATH, 'checkpoint.txt')

try :
    f = open(CHECK_PATH, "r")
    last_check = f.read()
    print("Last recorded checkpoint : ", last_check)
    f.close()
except :
    print("no previous record found.")

start_point = eval(input("Enter Start point : "))
end_point = eval(input("Enter end point : "))

dataframe = pd.read_csv(DB_PATH)

if start_point < 0 or start_point > len(dataframe):
    start_point = 0
    print("Start point : ", start_point)

if end_point < 0 or end_point > len(dataframe):
    end_point = len(dataframe)
    print("End point : ", end_point)

male_count = 0
female_count = 0

for cursor in range(start_point, end_point):
    print(cursor)
    row = dataframe.iloc[cursor]
    img = cv.imread(os.path.join(IMG_PATH, str(row['parent_id']), str(row['pk']), row['img']))
    if row['classification'] == 0 :
        cv.imwrite(os.path.join(SAVE_PATH, 'F' + '_' + str(female_count) + '.png'), img)
        female_count += 1
    elif row['classification'] == 1 :
        cv.imwrite(os.path.join(SAVE_PATH, 'M' + '_' + str(male_count) + '.png'), img)
        male_count += 1
    else :
        continue

print(" Total Saved count. ")
print("Male Count   : ", male_count)
print("Female Count : ", female_count)
input("Press any key to exit!")
