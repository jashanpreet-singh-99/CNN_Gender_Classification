import json
import codecs
import datetime
import os
import pandas as pd
from instagram_web_api import Client

web_api = Client(auto_patch=False, drop_incompat_key=False)
#web_api = Client(auto_patch=True, authenticate=True, username='Ck_Techo', password='jashan17ck')
user_feed_info = web_api.user_feed('44759974768', count=1)
data_list = []
print(user_feed_info)
for data in user_feed_info :
    data_dict = {}
    data = data['node']
    _id = data['id']
    _url = data['display_url']
    _is_video = data['is_video']
    data_dict['id'] = _id
    data_dict['url'] = _url
    if not _is_video :
        print(data)
        print(_id,_url)
        data_list.append(data_dict)
    print()
    break
print("Final entries",len(data_list))

