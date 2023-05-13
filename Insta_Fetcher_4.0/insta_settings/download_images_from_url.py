import requests
import time
import os
import numpy as np
import pandas as pd

PATH = os.getcwd() + '/images/'

content_dict = {}

count = 0

"""
Load the meta-data from the compiled master record
"""

image_dataset = pd.read_csv('dataset/master_feed_dataset.csv')

print(image_dataset.columns)

"""
Create the required folders to form the desired structure
and
Generate the content lists of already downloaded contents
"""

if not os.path.isdir(PATH) :
        os.mkdir(PATH)
        print("Directory Generated.")

parent_ids = image_dataset['parent_id'].unique()
print("Parent ids : ", len(parent_ids))

for parent_id in parent_ids :
    if not os.path.isdir(PATH + str(parent_id)) :
        os.mkdir(PATH + str(parent_id))
    content_dict[parent_id] = os.listdir(PATH + str(parent_id))
print("Folder structure and content lists updated.")

"""
start downloading and perfrom thge required checks
"""

for index, row in image_dataset.iterrows():
    url = row['url']
    if pd.isnull(url) :
        print("Problematic address : ", url)
        continue
    
    pk = row['pk']
    parent_id = row['parent_id']
    
    if (str(pk) + ".png") in content_dict[parent_id] :
        print("Already Downloaded")
        continue

    try :
        filepath = PATH + str(parent_id) + "/" + str(pk) + ".png"
        r = requests.get(url, allow_redirects=True)
        open(filepath, 'wb').write(r.content)
        print("Downloaded Image : ", count)
        count += 1
    except :
        print("Error while downloading : ", count)
        time.sleep(5)
