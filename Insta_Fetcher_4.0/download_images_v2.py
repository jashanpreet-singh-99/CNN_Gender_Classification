import requests
import time
import os
import numpy as np
import pandas as pd
import concurrent.futures


IMG_PATH = os.path.join(os.getcwd(), 'images')
DATASET_PATH = os.path.join(os.getcwd(), 'dataset_master')

if not os.path.isdir(IMG_PATH) :
        os.mkdir(IMG_PATH)
        print("Directory Generated.")

def get_master_dataset(set_id):
        return os.path.join(DATASET_PATH, 'master_batch_' + str(set_id) + '.csv')

def download_batch(batch_id):
        content_dict = {}
        count = 0
        """
        Load the meta-data from the compiled master record
        """
        image_dataset = pd.read_csv(get_master_dataset(batch_id))    

        """
        Create the required folders to form the desired structure
        and
        Generate the content lists of already downloaded contents
        """

        parent_ids = image_dataset['parent_id'].unique()
        print("Parent ids : ", len(parent_ids))

        for parent_id in parent_ids :
                dir_path = os.path.join(IMG_PATH, str(parent_id))
                if not os.path.isdir(dir_path) :
                        os.mkdir(dir_path)
                content_dict[parent_id] = os.listdir(dir_path)
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
            file_name = str(pk) + ".png"

            if file_name in content_dict[parent_id] :
                print("Already Downloaded")
                continue
            try :
                filepath = os.path.join(IMG_PATH, str(parent_id), file_name)
                r = requests.get(url, allow_redirects=True)
                open(filepath, 'wb').write(r.content)
                print("Thread :", batch_id,"Downloaded Image : ", count)
                count += 1
            except :
                print("Error while downloading : ", count)
                time.sleep(5)
        return batch_id

def main():
        """ Starting Different Threads """
        master_dir_files = os.listdir(DATASET_PATH)
        batches = 0
        for file in master_dir_files:
                if file.startswith('master_batch'):
                        batches += 1
        print("Batches Found in master dir :", batches)

        with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(download_batch, range(batches))
                [print("Done : ",r) for r in results]

print("Completed Downloads.")

if __name__ == '__main__':
    main()
