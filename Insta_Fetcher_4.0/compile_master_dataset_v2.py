import os
import pandas as pd

MASTER_DATASET_PATH = os.path.join(os.getcwd(), 'dataset_master')
DATASET_PATH = os.path.join(os.getcwd(), 'dataset')
IMG_PATH = os.path.join(os.getcwd(), 'images')

COLUMNS = ['pk', 'id', 'taken_at', 'media_type', 'lat', 'lng', 'img_width', 'img_height', 'url']

def remove_extension(file) :
    return file.split('.')[0]

" Create Blank Dataset "
master_dataframe = pd.DataFrame(columns=COLUMNS)

" List of all datasets available "
url_datsets = os.listdir(DATASET_PATH)

" Compile all the dataset into 1 "
for i,url_file in enumerate(url_datsets) :
    print("Compiling dataset number : ", i)
    dataset = pd.read_csv(os.path.join(DATASET_PATH, url_file))
    parent_id = url_file.split('~')[0]
    dataset['parent_id'] = parent_id
    master_dataframe = master_dataframe.append(dataset, ignore_index=True)

print("Toatl Records Compiled Before pre-processing : ", len(master_dataframe))    

"""
Pre-process Master dataset
# sort dataset
# remove duplicates
# drop Nan urls
"""
master_dataframe.sort_values("id", inplace=True)
master_dataframe.drop_duplicates(subset="id", keep=False, inplace=True)
master_dataframe = master_dataframe.dropna(subset=['url'])

img = {}
" Already images data"
img_folders = os.listdir(IMG_PATH)
print("Folders : ", len(img_folders))
for folder in img_folders:
    data = os.listdir(os.path.join(IMG_PATH, folder))
    img[folder] = list(map(remove_extension, data))

remove_records = []
" Remove if already downloaded images "
for index,row in master_dataframe.iterrows():
    parent_id = row['parent_id']
    pk = row['pk']
    if str(parent_id) in img_folders and str(pk) in img[parent_id] :
        remove_records.append(index)
print("Removal records : ", len(remove_records))
" Remove records "
master_dataframe.drop(remove_records, inplace=True)

print("Toatl Records Compiled : ", len(master_dataframe))

" Check if the master dataset is not empty! "
if len(master_dataframe) > 0:

    " Get value count of each parent_id "
    value_counts = dict(master_dataframe['parent_id'].value_counts())

    " Init essentail var "
    DIV_COUNT = eval(input("Enter number of divisions. : "))
    ELEMENT = len(master_dataframe)/DIV_COUNT

    " As per the Initialized vars distribute then into batches "
    div_list = []
    l_t = {'count':0, 'elements':[]}
    for p_id,count in value_counts.items():
        l_t['count'] += count
        l_t['elements'].append(p_id)
        if l_t['count'] > ELEMENT :
            div_list.append(l_t)
            l_t = {'count':0, 'elements':[]}
    div_list.append(l_t)

    [print("Batch {0} : ids -> {1} : count -> {2}".format(x, len(div_list[x]['elements']), div_list[x]['count'])) for x in range(DIV_COUNT)]

    " Create dataset from the assigned batches. "
    for i,d_list in enumerate(div_list):
         dataset = master_dataframe[master_dataframe['parent_id'].isin(d_list['elements'])]
         dataset.reset_index(drop=True, inplace=True)
         dataset.to_csv(os.path.join(MASTER_DATASET_PATH, 'master_batch_' + str(i) + '.csv'))
         print("Batch saved {0} : {1}".format(i, len(dataset)))
else :
    print("Seems like the master dataset is emplty!")
input("Press any key to exit.")
