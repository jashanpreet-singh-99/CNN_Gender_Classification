import json
import codecs
import datetime
import os
import time
import pandas as pd
import numpy as np
from random import randrange
from instagram_private_api import ( Client, ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError, __version__ as client_version)

print("""
ck_dev        : ck_dev_2021
ck_techo      : Ck_Techo
gkaku_off     : gkaku_off
dll_90        : anneliese_dll_90
thea_1966     : thea_1966_8
""")
ch = input("Select account : ")

if ch == "ck_dev" :
    USERNAME = "ck_dev_2021"
    PASSWORD = "jashanCK@17"
    SETTINGS_PATH = os.getcwd() + "\\insta_settings\\settings_ck_dev.json"
elif ch == "ck_techo" :
    USERNAME = "Ck_Techo"
    PASSWORD = "jashan17"
    SETTINGS_PATH = os.getcwd() + "\\insta_settings\\settings_ck_techo.json"
elif ch == "gkaku_off" :
    USERNAME = "gkaku_off"
    PASSWORD = "jashan17GK"
    SETTINGS_PATH = os.getcwd() + "\\insta_settings\\settings_gkaku_off.json"
elif ch == "dll_90" :
    USERNAME = "anneliese_dll_90"
    PASSWORD = "jashan17"
    SETTINGS_PATH = os.getcwd() + "\\insta_settings\\settings_dll_90.json"
elif ch == "thea_1966" :
    USERNAME = "thea_1966_8"
    PASSWORD = "jashan17"
    SETTINGS_PATH = os.getcwd() + "\\insta_settings\\settings_thea_1966.json"


fetched_files = os.listdir("dataset/")

present_id_list = [x.split('~')[0] for x in fetched_files]

data_needed = ['pk', 'id', 'taken_at', 'media_type', 'lat', 'lng', 'image_versions2']
img_data_needed = ['width', 'height', 'url']
columns = ['pk', 'id', 'taken_at', 'media_type', 'lat', 'lng', 'img_width', 'img_height', 'url']

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes', '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')

def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object

def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

print('Client version: {0!s}'.format(client_version))

SETTINGS_FILE = SETTINGS_PATH
if not os.path.isfile(SETTINGS_FILE) :
    print("No settings file found.")

    api = Client(USERNAME, PASSWORD, on_login=lambda x: onlogin_callback(x, SETTINGS_PATH))
else :
    with open(SETTINGS_FILE) as file_data :
        cached_settings = json.load(file_data, object_hook=from_json)
    print('Resulting settings: {0!s}'.format(SETTINGS_FILE))
    api = Client(USERNAME, PASSWORD, settings=cached_settings)

cookie_expiry = api.cookie_jar.auth_expires
print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

master_user_id = api.authenticated_user_id
print("ID : ", master_user_id)
followers = api.user_following(master_user_id, api.generate_uuid())['users']

""" END of ESSENTIAL LOGIN STUFF """

"""
Check for previous user dataset
"""

USER_DATASET = 'dataset_user/users_details.csv'
try:
    user_db = pd.read_csv(USER_DATASET, index_col=0)
except :
    print("No previous records.")
    user_db = pd.DataFrame(columns=['pk', 'username', 'next_max_id', 'taken_at'])

user_data = []
list_feeds = []

print("Followers : ", len(followers))

total_feed_parsed = 0

for i,follower in enumerate(followers):
    user_error_count = 0
    _pk = follower['pk']
    _username = follower['username']
    
    print(_pk, _username)

    """
    Enter data in User dataset
    """
    user_dict = {}
    user_dict['pk'] = _pk
    user_dict['username'] = _username

    """
    Check for incomplete fetch due to ban
    """
    user_feed_dataset = []
    continue_prev = False
    next_max_id = 0
    if len(user_db[user_db['pk'] == _pk]) > 0 :
        if not pd.isna(user_db[user_db['pk'] == _pk]['next_max_id'].values[0]) :
            next_max_id = user_db[user_db['pk'] == _pk]['next_max_id'].values[0]
            continue_prev = True
            user_feed_dataset = pd.read_csv('dataset/' + str(_pk) + "~" + _username + '.csv', index_col=0)
            print("Loaded previously incomplete dataset.")

    """
    Fetching User's feed
    """
    try :
        if not next_max_id == 0 :
            print("next_max_id", next_max_id)
            m_user_feed = api.user_feed(_pk, max_id=next_max_id)
        else :
            m_user_feed = api.user_feed(_pk)
    except :
        print("Error, Probably banned.")
        continue

    """
    Get and save next_max_id
    """
    next_max_id = m_user_feed.get('next_max_id')
    user_dict['next_max_id'] = next_max_id
    
    user_feed = m_user_feed.get('items')
    print("User Feed Read : ", len(user_feed))
    
    list_feeds = []
    feed_count = len(user_feed)
    perform_timestamp_checks = False

    """
    Check If the repo is already latest
    """
    if len(user_db[user_db['pk'] == _pk]) > 0 :
        try :
            time_stamp = user_db[user_db['pk'] == _pk]['taken_at'].values[0]
            latest_feed_date = user_feed[0].get('taken_at')
            if latest_feed_date == time_stamp:
                print("Already up to date.")
                continue
            else :
                print("New data found")
                perform_timestamp_checks = True
        except :
            print("No Timestamp found")
    
    """
    Extracting Meta-Data from Batch_1 Feeds Fetched
    """
    for fi,feed in enumerate(user_feed) :
            dict_feed = {}
            if fi == 0 and not continue_prev:
                user_dict['taken_at'] = feed['taken_at']
            if perform_timestamp_checks :
                latest_feed_date = feed.get('taken_at')
                if latest_feed_date == time_stamp:
                    print("Reached previous checkpoint.")
                    break
            for key in data_needed :
                if key in feed.keys() :
                    if key == data_needed[-1] :
                        for k,v in feed[key]['candidates'][0].items():
                            if k in img_data_needed :
                                dict_feed[k] = v
                    else :
                        dict_feed[key] = feed[key]
            list_feeds.append(dict_feed)
            
    if perform_timestamp_checks :
        latest_feed_date = feed.get('taken_at')
        if latest_feed_date == time_stamp:
            print("Reached previous checkpoint.")
            continue
    
    while next_max_id :
        print("Current id : ", next_max_id, "Feeds so far : ", feed_count)
        try :
            m_user_feed = api.user_feed(_pk, max_id=next_max_id)
        except :
            print("Error in reading feeds")
            time.sleep(60)
            user_error_count += 1
            if user_error_count > 3 :
                break
            continue
        user_feed = m_user_feed.get('items')
        feed_count += len(user_feed)
        for feed in user_feed :
            dict_feed = {}
            if perform_timestamp_checks :
                latest_feed_date = feed.get('taken_at')
                if latest_feed_date == time_stamp:
                    print("Reached previous checkpoint.")
                    break
            for key in data_needed :
                if key in feed.keys() :
                    if key == data_needed[-1] :
                        for k,v in feed[key]['candidates'][0].items():
                            if k in img_data_needed :
                                dict_feed[k] = v
                    else :
                        dict_feed[key] = feed[key]
            list_feeds.append(dict_feed)
        try :
            if perform_timestamp_checks :
                if latest_feed_date == time_stamp:
                    print("Reached previous checkpoint.")
                    next_max_id = np.nan
                    break
            next_max_id = m_user_feed.get('next_max_id')
            user_dict['next_max_id'] = next_max_id
        except :
            print("no max id : ", m_user_feed.keys())
            break
        time.sleep(randrange(5))
    print("Managed feeds for far : ", len(list_feeds))
    """
    Save max_id for future
    """
    if len(user_db) > 0 and _pk in user_db['pk'].values :
        print("Alread exist.")
        user_db.at[user_db['pk'] == _pk, 'next_max_id'] = user_dict['next_max_id']
        if not continue_prev :
            user_db.at[user_db['pk'] == _pk, 'taken_at'] = user_dict['taken_at']
    else :
        user_db.loc[len(user_db)] = [_pk,_username, user_dict['next_max_id'], user_dict['taken_at']]
    """
    Save feed data.
    """
    user_feed_dataframe = pd.DataFrame(list_feeds)
    if len(user_feed_dataset) > 0 :
        user_feed_dataset = user_feed_dataset.append(user_feed_dataframe, ignore_index=True)
        user_feed_dataset.to_csv('dataset/' + str(_pk) + "~" + _username + '.csv')
        print("Updated user feed dataset : ", len(user_feed_dataset))
    else :
        user_feed_dataframe.to_csv('dataset/' + str(_pk) + "~" + _username + '.csv')
        print("Saved user feed dataset : ", len(user_feed_dataframe))
    print("DONE : ", i)
    total_feed_parsed += feed_count
print(len(list_feeds))
user_db.to_csv(USER_DATASET)
print("Total Feeds paresed : ", total_feed_parsed)
