import json
import codecs
import datetime
import os
import time
from instagram_private_api import Client

PATH_CREDENTAILS = os.path.join(os.getcwd(), 'credentials', 'cred_1')

"""
Fetch the creds array from the local disk.
"""
def get_credentials():
    creds = []
    file = open(PATH_CREDENTAILS, 'r')
    data = file.read()
    for cred in data.split('\n'):
        cred_dict = {}
        cred_list = cred.split('~')
        cred_dict['ch'] = cred_list[0]
        cred_dict['username'] = cred_list[1]
        cred_dict['password'] = cred_list[2]
        creds.append(cred_dict)
    print("Credentials Found : ", len(creds))
    return creds

"""
Generate the appropriate path based on the selected creds.
"""
def get_creds_settings_path(ch):
    return os.path.join(os.getcwd(), "insta_settings", "settings_" + ch + '.json')

" API UTILS "

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
        
" END OF API UTILS "

"""
# Fetch the local creds array
# ask for selection of cred
# as per the selected cred, get the cached settings and login to the server
-> API object
"""
def login():
    CREDS = get_credentials()
    [print('{0} - {1!s} : {2!s}'.format(i, c['ch'], c['username'])) for i,c in enumerate(CREDS)]
    ch = eval(input("Enter choice : "))
    user_creds = CREDS[ch]
    settings_path = get_creds_settings_path(user_creds['ch'])
    username = user_creds['username']
    password = user_creds['password']
    if not os.path.isfile(settings_path) :
        print("No settings file found.")
        api = Client(username, password, on_login=lambda x: onlogin_callback(x, settings_path))
    else :
        with open(settings_path) as file_data :
            cached_settings = json.load(file_data, object_hook=from_json)
        api = Client(username, password, settings=cached_settings)
        
    cookie_expiry = api.cookie_jar.auth_expires
    print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))
    return api
