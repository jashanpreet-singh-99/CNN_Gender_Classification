import os
import random
import cv2 as cv
import pandas as pd

DB_PATH = os.path.join(os.getcwd(), 'classification_db')
IMG_PATH = os.path.join(os.getcwd(), 'raw_faces')
CHECK_PATH = os.path.join(DB_PATH, 'checkpoint.txt')

SAVE_BATCH_SIZE = 200

if not os.path.isdir(DB_PATH) :
    os.mkdir(DB_PATH)

db_list = os.listdir(DB_PATH)

print("Databases found :", len(db_list))
[print("{0} : {1}".format(i,x)) for i,x in enumerate(db_list)]

def get_result(val):
    if val == 0:
        return 'F'
    elif val == 1:
        return 'M'
    else :
        return 'X'

ch = eval(input("""
Enter the option
0 : generate default_db from classification data
1 : copy previous db
"""))

if ch == 0 :
    try :
        f = open(CHECK_PATH, "r")
        last_check = f.read()
        print("Last recorded checkpoint : ", last_check)
        f.close()
    except :
        print("no previous record found.")
    ch = eval(input("Enter jump point : "))
    if ch >= 0:
        cursor = ch
    else :
        cursor = 0
    " Generate db from data "
    LOAD_PATH = os.path.join(DB_PATH, "DF_db_v1.0.csv")
    dataframe = pd.read_csv(LOAD_PATH, index_col=0)
    while cursor < len(dataframe):
        row = dataframe.iloc[cursor]
        classify = get_result(row['classification'])
        img = cv.imread(os.path.join(IMG_PATH, str(row['parent_id']), str(row['pk']), row['img']))
        img = cv.resize(img, (512,512))
        cv.putText(img , classify, (460,490), cv.FONT_HERSHEY_SIMPLEX, 2, 255, 6)
        while True:
            k = cv.waitKey(1)
            if k != -1 :
                print(cursor, ":")
            if k == ord('n') :
                dataframe.at[cursor, 'mode'] = 'M'
                cursor += 1
                if cursor == len(dataframe):
                    cursor -= 1
                    print("All Done")
                cv.destroyAllWindows()
                break;
            if k == ord('b') :
                cursor -= 1
                row = dataframe.iloc[cursor]
                if cursor < 0:
                    cursor = 0
                cv.destroyAllWindows()
                break;
            if k == ord('s') :
                new_val = int(not bool(row['classification']))
                dataframe.at[cursor, 'classification'] = new_val
                break
            if k == ord('x') :
                dataframe.at[cursor, 'classification'] = -1
                break
            cv.imshow('img', img)
        if (cursor % SAVE_BATCH_SIZE) == 0:
            dataframe.to_csv(LOAD_PATH)
            print("Saved.")
            f = open(CHECK_PATH, "w")
            f.write(str(cursor))
            f.close()
