import json
import codecs
import datetime
import os
import time
import pandas as pd
from instagram_private_api import ( Client, ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError, __version__ as client_version)

USERNAME = "Ck_Techo"
PASSWORD = "jashan17ck"

SETTINGS_PATH = os.getcwd() + "\\insta_settings\\settings.json"

fetched_files = os.listdir("dataset/")

present_id_list = [x.split('~')[0] for x in fetched_files]

data_needed = ['pk', 'id', 'device_timestamp', 'media_type', 'lat', 'lng', 'image_versions2']
img_data_needed = ['width', 'height', 'url']
columns = ['pk', 'id', 'device_timestamp', 'media_type', 'lat', 'lng', 'img_width', 'img_height', 'url']

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
device_id = None

SETTINGS_FILE = SETTINGS_PATH
if not os.path.isfile(SETTINGS_FILE) :
    print("No settings file found.")

    api = Client(USERNAME, PASSWORD, on_login=lambda x: onlogin_callback(x, SETTINGS_PATH))
else :
    with open(SETTINGS_FILE) as file_data :
        cached_settings = json.load(file_data, object_hook=from_json)
    print('Resulting settings: {0!s}'.format(SETTINGS_FILE))

    device_id = cached_settings.get('device_id')
    api = Client(USERNAME, PASSWORD, settings=cached_settings)

cookie_expiry = api.cookie_jar.auth_expires
print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

master_user_id = api.authenticated_user_id
print("ID : ", master_user_id)

followers = api.user_following(master_user_id, api.generate_uuid())['users']
user_data = []
list_feeds = []

print(len(followers))
total_feed_parsed = 0

for i,follower in enumerate(followers):
    user_error_count = 0
    _pk = follower['pk']
    _username = follower['username']
    if str(_pk) in present_id_list :
        print("Already pesent.")
        continue
    print(_pk, _username)
    user_dict = {}
    user_dict['pk'] = _pk
    user_dict['username'] = _username
    user_data.append(user_dict)

    try :
        m_user_feed = api.user_feed(_pk)
    except :
        print("Error")
        continue
    
    next_max_id = m_user_feed.get('next_max_id')
    user_feed = m_user_feed.get('items')
    print(len(user_feed))
    list_feeds = []

    feed_count = len(user_feed)
    for feed in user_feed :
            dict_feed = {}
            for key in data_needed :
                if key in feed.keys() :
                    if key == data_needed[-1] :
                        for k,v in feed[key]['candidates'][0].items():
                            if k in img_data_needed :
                                dict_feed[k] = v
                    else :
                        dict_feed[key] = feed[key]
            list_feeds.append(dict_feed)
    
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
            next_max_id = m_user_feed.get('next_max_id')
        except :
            print("no max id : ", m_user_feed.keys())
            break
        time.sleep(20)
        if feed_count > 2000 :
            break
    print(len(list_feeds))
    user_feed_dataframe = pd.DataFrame(list_feeds)
    user_feed_dataframe.to_csv('dataset/' + str(_pk) + "~" + _username + '.csv')
    print("DONE : ", i)
    total_feed_parsed += feed_count
print(len(list_feeds))
user_dataframe = pd.DataFrame(user_data)
user_dataframe.to_csv('dataset_user/users_details.csv')
print("Total Feeds paresed Before Error : ", total_feed_parsed)
