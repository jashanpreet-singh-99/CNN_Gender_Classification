import json
import codecs
import datetime
import os
import time
import pandas as pd
import numpy as np
from random import randrange
from instagram_private_api import Client
import utils.insta_utils as i_utils
import utils.dataset_utils as d_utils

"""
Login to instagram creds and return the Client API object.
-> | API object : api
"""
api = i_utils.login()

"""
# Fetch the followers list.
# Save then to local disk with default values -1
-> | user_db : dataset with metadata of each user.
"""
user_id = api.authenticated_user_id
followers = api.user_following(user_id, api.generate_uuid())['users']
user_db = d_utils.save_followers_dataset(followers)

"""
Iterate over each follower.
# load previous saved feed db or create a new one
# fetch old_time_stamp

"""

print("Current available points :",len(user_db))
ch_jump = eval(input("Enter followers jump point : "))

if ch_jump > len(user_db) :
    print("Invalid jump point. Going with the default.")
    ch_jump = 0

for index,follower in user_db.iterrows():
    if index < ch_jump:
        continue
    
    is_incomplete = False
    is_outdated = False

    pk = follower.get('pk')
    username = follower.get('username')
    feed_db, taken_at = d_utils.user_pre_dataset_check(follower)
    next_max_id = follower.get('next_max_id')

    " INCOMPLETE FLAG ASSIGNED "
    if next_max_id == -1 or pd.isna(next_max_id) :
        is_complete = False
    else :
        is_incomplete = True

    " FETCH FEED BATCH_1 "
    try :
        user_feed_batch = api.user_feed(pk)
        time.sleep(randrange(5))
    except Exception as e:
        print("Error in Fetching First Feed. Probably Banned")
        print(e)
        continue

    """
    Check if the batch has some content or not
    """
    if len(user_feed_batch.get('items')) < 1:
        print("Unable to fetch the data. Batch Empty!")
        continue

    " FEED META-DATA "
    latest_taken_at = user_feed_batch.get('items')[0].get('taken_at')
    latest_next_max_id = user_feed_batch.get('next_max_id')

    " OUTDATED FLAG ASSIGNED "
    if latest_taken_at > taken_at:
        is_outdated = True
    else :
        is_outdated = False

    print("FLAGS :")
    print("OUTDATED   :", is_outdated)
    print("INCOMPLETE :", is_incomplete)
    
    " SAVE LATEST TAKEN AT IN USER-DB "
    user_db = d_utils.update_user_db_taken_at(user_db, pk, latest_taken_at)

    " COVER UP THE MISSING DATA OR NEW DATA "
    error_count = 0
    while is_outdated and latest_next_max_id:
        latest_next_max_id = user_feed_batch.get('next_max_id')
        
        " PROCESS FEEDS "
        feed_db, is_outdated = d_utils.procress_outdated_feed_batch(feed_db, user_feed_batch.get('items'), taken_at)
        
        " SAVE DATA IN LOCAL DISK "
        d_utils.save_feed_data(feed_db, pk, username)
        
        " UPDATE THE NEXT_MAX_ID "
        user_db = d_utils.update_user_db_next_max_id(user_db, pk, latest_next_max_id)
        
        " FETCH NEXT BATCH "
        try :
            user_feed_batch = api.user_feed(pk, max_id=latest_next_max_id)
        except :
            print("Error Fetching Feed.")
            error_count += 1
            if error_count > 3:
                    break
            else :
                time.sleep(randrange(60))
        
        time.sleep(randrange(5))

    print("COMPLETED OUTDATED CYCLE, ALL FEEDS ARE UPDATED.")

    " JUMP TO LAST RECORDED COMPLETED SECTION "
    error_count = 0
    if is_incomplete :
        
        find_next_max_id = False

        while next_max_id:
            try :
                user_feed_batch = api.user_feed(pk, max_id=next_max_id)
            except :
                print("Error in Fetching Frst Feed. Probably Banned")
                error_count += 1
                if error_count > 3:
                    break
                else :
                    time.sleep(randrange(60))
            " PROCESS FEEDS "
            feed_db, find_next_max_id = d_utils.procress_feed_batch(feed_db, user_feed_batch.get('items'))

            " SAVE DATA IN LOCAL DISK "
            d_utils.save_feed_data(feed_db, pk, username)

            if not find_next_max_id :
                " CONTINUE BATCH "
                next_max_id = user_feed_batch.get('next_max_id')
            else :
                next_max_id = d_utils.find_next_max_id_from_db(feed_db)
                find_next_max_id = False
                " FIND NEXT_MAX_ID"
                

            " UPDATE THE NEXT_MAX_ID "
            user_db = d_utils.update_user_db_next_max_id(user_db, pk, next_max_id)
            time.sleep(randrange(5))
        
    print("Users Done : ", index, " : ", username)
input("Press any key to exit.")
