import os
import pandas as pd

USER_DB_COLUMNS = ['pk', 'username', 'taken_at', 'next_max_id']

FEED_DB_COLUMNS = ['pk', 'id', 'taken_at', 'media_type', 'width' , 'height', 'url', 'lat', 'lng']

USER_DB_PATH_ROOT = os.path.join(os.getcwd(), "dataset_master")
USER_DB_PATH = os.path.join(USER_DB_PATH_ROOT, "users.csv")

FOLLOWER_FEED_PATH_ROOT = os.path.join(os.getcwd(), "dataset")

DATA_NEEDED = ['pk', 'id', 'taken_at', 'media_type', 'lat', 'lng', 'image_versions2']
IMG_DATA_NEEDED = ['width', 'height', 'url']

"""
# Save Follower's list to local disk with default values -1
-> | user_db : dataset with metadata of each user.
"""
def save_followers_dataset(followers):
    if os.path.exists(USER_DB_PATH) :
        user_db = pd.read_csv(USER_DB_PATH, index_col=0)
        print("Reading previously stored User_db.")
    else :
        if not os.path.isdir(USER_DB_PATH_ROOT) :
            os.mkdir(USER_DB_PATH_ROOT)
        user_db = pd.DataFrame(columns=USER_DB_COLUMNS)
        print("No User_db found. Creating a new one")
    for follower in followers:
        if follower['pk'] in user_db['pk'].values :
            continue
        user_dict = {}
        user_dict['pk'] = follower['pk']
        user_dict['username'] = follower['username']
        user_dict['taken_at'] = -1
        user_dict['next_max_id'] = -1
        user_db = user_db.append(user_dict, ignore_index=True)
    user_db.to_csv(USER_DB_PATH)
    print("All user data updated.", len(user_db))
    return user_db

"""
save user_db
"""
def save_user_db(db):
    db.to_csv(USER_DB_PATH)

"""
#For given follower check is old data is present
#if not then creatre a temp one (in memory)
-> | follower_feed_db : database of previously stored feeds
-> | taken_at : latest taken_at timestamp 
"""
def user_pre_dataset_check(follower):
    pk = follower['pk']
    username = follower['username']
    FOLLOWER_FEED_PATH = os.path.join(FOLLOWER_FEED_PATH_ROOT, str(pk) + "~" + username + ".csv")
    if os.path.exists(FOLLOWER_FEED_PATH) :
        follower_db = pd.read_csv(FOLLOWER_FEED_PATH, index_col=0)
        taken_at = follower_db['taken_at'].max()
        #print("Reading previously stored Follower`s feed db.")
    else :
        if not os.path.isdir(FOLLOWER_FEED_PATH_ROOT) :
            os.mkdir(FOLLOWER_FEED_PATH_ROOT)
        follower_db = pd.DataFrame(columns=FEED_DB_COLUMNS)
        taken_at = -1
        print("No feed_db found. Creating a new one")
    return (follower_db, taken_at)

"""
Update user_db next_max_id value
"""
def update_user_db_next_max_id(user_db, pk, next_max_id):
    user_db.at[user_db['pk'] == pk, 'next_max_id'] = next_max_id
    save_user_db(user_db)
    return user_db

"""
Update user_db taken_at value
"""
def update_user_db_taken_at(user_db, pk, taken_at):
    user_db.at[user_db['pk'] == pk, 'taken_at'] = taken_at
    save_user_db(user_db)
    return user_db

"""
<- | db : previously fetched feeds db
<- | batch : batch fetched from the API
<- | prev_taken_at : last taken_at stored in db
Process feed's meta-data from fetched_batch
"""
def procress_outdated_feed_batch(db, batch, prev_taken_at):
    outdated = True
    for feed in batch:
        if feed['taken_at'] > prev_taken_at :
            """ Check if already in db """
            if feed['pk'] in db['pk'].values :
                continue
            dict_feed = {}
            for key in DATA_NEEDED :
                if key in feed.keys() :
                    if key == DATA_NEEDED[-1] :
                        for k,v in feed[key]['candidates'][0].items():
                            if k in IMG_DATA_NEEDED :
                                dict_feed[k] = v
                    else :
                        dict_feed[key] = feed[key]
            db = db.append(dict_feed, ignore_index=True)        
        else :
            outdated = False
            break
    print("Parsing feeds :", len(db))
    return (db, outdated)

"""
Save feed onto the Disk
"""
def save_feed_data(db, pk, username):
    FOLLOWER_FEED_PATH = os.path.join(FOLLOWER_FEED_PATH_ROOT, str(pk) + "~" + username + ".csv")
    db.to_csv(FOLLOWER_FEED_PATH)

"""
<- | db : previously fetched feeds db
<- | batch : batch fetched from the API
Process feed's meta-data from fetched_batch
"""
def procress_feed_batch(db, batch):
    present_count = 0
    COUNT_LIMIT = 5
    find_next_max_id = False
    for feed in batch:
        """ Check if already in db """
        if feed['pk'] in db['pk'].values :
            present_count += 1
            if present_count > COUNT_LIMIT:
                find_next_max_id = True
            continue
        dict_feed = {}
        for key in DATA_NEEDED :
            if key in feed.keys() :
                if key == DATA_NEEDED[-1] :
                    for k,v in feed[key]['candidates'][0].items():
                        if k in IMG_DATA_NEEDED :
                            dict_feed[k] = v
                else :
                    dict_feed[key] = feed[key]
        db = db.append(dict_feed, ignore_index=True)
    print("Parsing feeds :", len(db))
    return (db, find_next_max_id)

"""
Find next_max_id 
"""
def find_next_max_id_from_db(feed_db):
    feed_db.sort_values("taken_at", axis = 0, ascending = False, inplace = True, na_position ='first')
    feed_db.reset_index(drop=True, inplace=True)
    next_max_id = feed_db.loc[len(feed_db) - 1,'id']
    return next_max_id
    
    
