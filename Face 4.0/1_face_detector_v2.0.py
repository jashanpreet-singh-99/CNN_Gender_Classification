import os
import cv2 as cv
import numpy as np
import concurrent.futures

CAFFE_MODEL = 'classifiers/face_detector.caffemodel'
PRO_TEXT    = 'classifiers/deploy.prototxt.txt'
net = cv.dnn.readNetFromCaffe(PRO_TEXT, CAFFE_MODEL)

IMG_PATH      = os.path.join(os.getcwd(), 'images')
IMG_SAVE_PATH = os.path.join(os.getcwd(), 'raw_faces')
PATHS = ['classified_images_##', 'images', 'raw_faces', 'test_##_##', 'train_##_##']

" Generate the required structure "
for folder in PATHS :
    if not os.path.isdir(os.path.join(os.getcwd(), folder)) :
        os.mkdir(folder)



def process_batch(batch_id, batch):
    saved_face = 0
    print("Processing : ", batch_id)
    for file in batch :
        img = cv.imread(file['load'])
        
        if isinstance(img, type(None)):
            continue
        
        HEIGHT, WIDTH = img.shape[:2]
        
        blob = cv.dnn.blobFromImage(cv.resize(img, (300,300)), 1.0, (300,300), (104.0, 177.0,123.0))
        
        net.setInput(blob)
        detections = net.forward()
        f_count = 0
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
        
            if confidence > 0.98:
                box = detections[0, 0, i, 3:7] * np.array([WIDTH, HEIGHT, WIDTH, HEIGHT])
                w = box[2] - box[0]
                h = box[3] - box[1]
                element = w/2 if w > h else h/2
                startX, startY, endX, endY = box.astype("int")
                startX = int(startX - element)
                if startX < 0 :
                    startX = 0
                startY = int(startY - element)
                if startY < 0 :
                    startY = 0
                endX = int(endX + element)
                if endX > WIDTH :
                    endX = WIDTH
                endY = int(endY + element)
                if endY > HEIGHT:
                    endY = HEIGHT
                face_img = img[startY:endY, startX:endX]
                if face_img.shape[0] > face_img.shape[1] :
                    dif = int((face_img.shape[0] - face_img.shape[1])/2)
                    startY = startY + dif
                    endY = endY - dif
                    face_img = img[startY:endY, startX:endX]
                elif face_img.shape[1] > face_img.shape[0] :
                    dif = int((face_img.shape[1] - face_img.shape[0])/2)
                    startX = startX + dif
                    endX = endX - dif
                    face_img = img[startY:endY, startX:endX]
                try :
                    face_img = cv.cvtColor(face_img, cv.COLOR_BGR2GRAY)
                    face_img = cv.resize(face_img, (128,128))
                    " Create IMG folder"
                    if not os.path.isdir(file['save']):
                        os.makedirs(file['save'])
                    print("Btach [", batch_id ,"] Face Number :", saved_face, " Confidence :", confidence)
                    cv.imwrite(os.path.join(file['save'], str(f_count) + '.png'), face_img)
                    f_count += 1
                    saved_face += 1
                except:
                    print("Error while saving.", file)

def helper(args):
    print("Called Batch {0} : {1}".format(args[0], len(args[1])))
    process_batch(args[0], args[1])

def main():
    " Ask for the processes to init "
    DIV_COUNT = eval(input("Enter the number of processes : "))

    img_folders = os.listdir(IMG_PATH)
    raw_folders = os.listdir(IMG_SAVE_PATH)

    " alreaady extracted faces "
    done_img = {}
    for folder in raw_folders:
        done_img[folder] = os.listdir(os.path.join(IMG_SAVE_PATH, folder))

    """
    Function to add parental id to the img_path
    """
    def add_parent_id(img, parent_id):
        " Prevent entry of already processed images "
        if parent_id in done_img.keys() and str(img[:-4]) in done_img[parent_id]:
            return 0
        else :
            p_dic = {}
            p_dic['load'] = os.path.join(IMG_PATH, parent_id, img)
            p_dic['save'] = os.path.join(IMG_SAVE_PATH, parent_id, img[:-4])
            return p_dic
        
    img_list = []
    for folder in img_folders:
        temp = os.listdir(os.path.join(IMG_PATH, folder))
        temp = list(map(add_parent_id, temp, [folder] * len(temp)))
        img_list.extend(temp)

    " remove 0 from list "
    print("total List size : ", len(img_list))
    img_list = [x for x in img_list if x != 0]
    print("Total images : ", len(img_list))

    batches = {}
    BATCH_SIZE = int(len(img_list)/DIV_COUNT)

    start = 0
    end = BATCH_SIZE
    for i in range(DIV_COUNT) :
        if end >= len(img_list) - 1 :
            batches[i] = img_list[start:]
        else :
            batches[i] = img_list[start:end]
        start = end
        end += BATCH_SIZE
    [print("Batch {0} Size : {1}".format(i, len(batches[i]))) for i in range(DIV_COUNT)]
    
    """ Starting Different Processes """
    print("Starting Main")
    args = [(x,batches[x]) for x in range(DIV_COUNT)]
    print("Args List : ", len(args))
    with concurrent.futures.ProcessPoolExecutor(max_workers=DIV_COUNT) as executor:
            results = executor.map(helper, args)
            [print("Done : ",r) for r in results]

    print("Completed Processing.")

if __name__ == '__main__':
    main()
