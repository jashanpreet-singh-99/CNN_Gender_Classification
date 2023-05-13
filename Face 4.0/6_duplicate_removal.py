import os
import cv2 as cv
import pandas as pd

IMG_PATH = os.path.join(os.getcwd(), 'db_images')


def dhash(img, hashsize=16):
    resized = cv.resize(img, (hashsize + 1, hashsize))
    diff = resized[:, 1:] > resized[:, :-1]
    return sum([2 ** i for (i,v) in enumerate(diff.flatten()) if v])

img_list = os.listdir(IMG_PATH)

hash_log = {}

for i,img_p in enumerate(img_list):
    print(i)
    path = os.path.join(IMG_PATH, img_p)
    img = cv.imread(path, 0)
    h = dhash(img)
    p = hash_log.get(h, [])
    if len(p) > 0:
        print("Duplicate : ", path)
        os.remove(path)
        continue
    p.append(path)
    hash_log[h] = p

print("Images remaining :", len(hash_log.keys()))
