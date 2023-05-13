import os
import cv2 as cv
import pandas as pd

IMG_PATH = os.path.join(os.getcwd(), 'db_images')
SAVE_PATH = os.path.join(os.getcwd(), 'train')

img_list = os.listdir(IMG_PATH)

male_img = []
female_img = []

for img_p in img_list:
    if img_p[0] == 'M':
        male_img.append(os.path.join(IMG_PATH, img_p))
    else :
        female_img.append(os.path.join(IMG_PATH, img_p))

print("Male Count   : ", len(male_img))
print("Female Count : ", len(female_img))

max_val = eval(input("Enter the max value : "))

for i in range(max_val):
    print("Processing :", i)
    img_m = cv.imread(male_img[i], 0)
    cv.imwrite(os.path.join(SAVE_PATH, 'M_' + str(i) + ".png"),img_m)
    img_f = cv.imread(female_img[i], 0)
    cv.imwrite(os.path.join(SAVE_PATH, 'F_' + str(i) + ".png"),img_f)

input("Press any key to exit!")
